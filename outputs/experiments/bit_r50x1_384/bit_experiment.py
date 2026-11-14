"""BiT-M R50x1 (ImageNet-21k ResNet-50) with the delivered notebook's binary recipe (384 px, 2 + 10 epochs,
metadata, dropout 0.3, weight decay 0.05, mild augmentation). Stem + stages 0-1 stay frozen (speed on M4).
Run from code/: bit_experiment.py <notebook> <scratch dir> <bit weights .h5>"""
import json, sys
import matplotlib
matplotlib.use("Agg")
nb_path, scratch, bit_weights = sys.argv[1:4]
sys.path.insert(0, scratch)
nb = json.load(open(nb_path)); src = lambda i: "".join(nb["cells"][i]["source"])
g = {}
exec(src(2), g)
cell4 = src(4)
assert 'RUN_DIR = OUT_DIR / f"run_{IMG_SIZE}px_binary_v3"' in cell4 and "IMG_SIZE = 384" in cell4
exec(cell4.replace('RUN_DIR = OUT_DIR / f"run_{IMG_SIZE}px_binary_v3"', 'RUN_DIR = OUT_DIR / "experiments" / "bit_r50x1_384"'), g)
g["save_figure"] = lambda name: None
for i in (10, 11, 13, 14, 16):
    exec(src(i), g)

from bit_keras import build_bit_r50
keras, np, pd = g["keras"], g["np"], g["pd"]
IMG_SIZE = g["IMG_SIZE"]
base_model = build_bit_r50((IMG_SIZE, IMG_SIZE, 3))
base_model.load_weights(bit_weights)
base_model.trainable = False
image_input = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="image")
metadata_input = keras.Input(shape=(g["NUM_METADATA"],), name="metadata")
x = g["augmentation"](image_input)
x = keras.layers.Rescaling(1 / 127.5, offset=-1, name="bit_preprocessing")(x)   # BiT expects [-1, 1]
x = base_model(x)
x = keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
x = keras.layers.Dropout(g["DROPOUT"], name="dropout")(x)
x = keras.layers.Concatenate(name="image_and_metadata")([x, metadata_input])
logits = keras.layers.Dense(g["NUM_CLASSES"], name="logits")(x)
outputs = keras.layers.Softmax(name="probabilities")(logits)
model = keras.Model({"image": image_input, "metadata": metadata_input}, outputs, name="bit_r50x1_skin_lesion")
g["base_model"], g["model"] = base_model, model

exec(src(28), g)    # learning-rate schedule, history, callbacks
exec(src(29), g)    # stage 1: head only

# Stage 2: fine-tune stages 2-3 and the final norm (stem + stages 0-1 frozen)
base_model.trainable = True
for layer in base_model.layers:
    layer.trainable = not layer.name.startswith(("stem", "stages_0", "stages_1"))
print("Trainable weights in stage 2:", sum(int(np.prod(w.shape)) for w in model.trainable_weights), flush=True)
model.compile(optimizer=keras.optimizers.Adam(g["FINE_TUNE_LR"], weight_decay=g["WEIGHT_DECAY"]),
              loss=g["loss_fn"], metrics=["accuracy"])
if len(g["read_history"]()) < g["TOTAL_EPOCHS"]:
    model.fit(g["train_ds"], validation_data=g["val_ds"], initial_epoch=g["HEAD_EPOCHS"], epochs=g["TOTAL_EPOCHS"],
              callbacks=g["training_callbacks"]("backup_stage2"), verbose=2)
history = g["read_history"]()
print(history.round(4).to_string(index=False), flush=True)

# Evaluate the best weights once
model.load_weights(g["BEST_WEIGHTS"])
lines = []
for name, df, ds in [("val", g["val_df"], g["val_ds"]), ("test", g["test_df"], g["test_ds"])]:
    pred = model.predict(ds, verbose=0).argmax(1)
    correct = pred == df["y"].to_numpy()
    seen = df["lesion_id"].isin(g["ham_train"]["lesion_id"]).to_numpy()
    mal = df["y"].to_numpy() == 1
    lines.append(f"{name}: accuracy {correct.mean():.4f} | malignant recall {correct[mal].mean():.4f} | "
                 f"new lesions {correct[~seen].mean():.4f} | seen lesions {correct[seen].mean():.4f}")
tr = g["train_df"]
ham = tr[tr["source"] == "HAM10000"].sample(min(2000, (tr["source"] == "HAM10000").sum()), random_state=0)
model.compile(loss="categorical_crossentropy", metrics=["accuracy"])
lines.append(f"train HAM10000 (no augmentation): {model.evaluate(g['make_dataset'](ham), verbose=0)[1]:.4f}")
best = history.loc[history["val_accuracy"].idxmax()]
lines.insert(0, f"best epoch {int(best['epoch']) + 1}: val_accuracy {best['val_accuracy']:.4f}")
text = "\n".join(lines)
print(text)
(g["RUN_DIR"] / "result.txt").write_text(text + "\n")
