# Group 8 - ISIC Skin Lesion Classification (Benign vs Malignant)

Coding component of the CSC60904 Deep Learning group assignment (domain option A: medical imaging).
The project classifies dermoscopy images of skin lesions as **benign** or **malignant** with two
ResNet-50 models and averages their predictions.

The whole implementation is one Jupyter notebook: [`code/Group_8_Image_Recognition.ipynb`](code/Group_8_Image_Recognition.ipynb).

## Technical specification

### Task

| Class | Diagnoses (dataset codes) |
|-------|---------------------------|
| Malignant | MEL melanoma, BCC basal cell carcinoma, AKIEC actinic keratosis / intraepithelial carcinoma, SCC squamous cell carcinoma |
| Benign | NV melanocytic nevus, BKL benign keratosis-like lesion, DF dermatofibroma, VASC vascular lesion |

Images with the unknown diagnosis (UNK) are dropped. The detailed diagnosis is kept for error analysis.

### Data

| Source | Role | Images used |
|--------|------|-------------|
| HAM10000 (ISIC 2018 Task 3) | split by image, stratified by diagnosis, 70 / 15 / 15 | 7,010 train / 1,502 validation / 1,503 test |
| ISIC 2019 training set | extra training data (its 10,015 HAM10000 images are removed) | 15,316 |
| BCN20000 (labelled part of the ISIC 2019 test set) | extra training data | 6,191 |

- Training set: 28,517 images, 41% malignant. Validation and test images come **only** from HAM10000.
- Always answering "Benign" scores 0.8049 on validation and 0.8051 on test. This is the baseline.
- **Data leakage:** because HAM10000 is split by image, not by lesion, about a third of the validation and
  test images show a lesion that has another photo in the training set. The notebook reports accuracy
  separately for new lesions and for lesions seen in training.
- Patient metadata is a second model input with 10 numbers: age / 100, an age-missing flag, male, female,
  and a one-hot body-site group (torso, head/neck, upper extremity, lower extremity, palms/soles, oral/genital).

### Models

Both models use the same head on top of the backbone:
global average pooling → dropout 0.3 → concatenate with the metadata → Dense(2) → softmax.

| | Model 1 | Model 2 |
|---|---|---|
| Backbone | Keras ResNet-50 | BiT-M R50x1 (pre-activation ResNet-50 v2 with GroupNorm and weight-standardised convolutions), built layer by layer in Keras |
| Pre-training | ImageNet-1k | ImageNet-21k ([`timm/resnetv2_50x1_bit.goog_in21k`](https://huggingface.co/timm/resnetv2_50x1_bit.goog_in21k), 273 MB, read with NumPy) |
| Input preprocessing | `keras.applications.resnet.preprocess_input` (RGB → BGR, ImageNet mean subtracted) | pixels scaled to [-1, 1] |
| Training size | 448 × 448 | 384 × 384 |
| Layers trained in stage 2 | whole backbone (BatchNorm frozen) | stages 2–3 (stem and stages 0–1 frozen) |

**Final model:** the average of the two models' softmax probabilities, with both models evaluated at
448 × 448. Each model uses its best-validation-accuracy epoch.

### Training recipe (same for both models)

| Setting | Value |
|---------|-------|
| Stage 1 | backbone frozen, train the head for 2 epochs, Adam 1e-3 |
| Stage 2 | fine-tune for 10 epochs, Adam 5e-5 with cosine decay to 1e-6 |
| Loss | categorical cross-entropy |
| Regularisation | dropout 0.3, Adam weight decay 0.05 |
| Augmentation (training only) | horizontal / vertical flip, rotation up to ±90°, zoom 15%, brightness / contrast 10% |
| Batch size | 16 |
| Model selection | best validation accuracy. The test set is used once, at the end. |
| Seed | 8 |

### Results (final run, 2 November 2026)

| Model | Validation | Test |
|-------|-----------:|-----:|
| ResNet-50 (ImageNet, 448 px) | 0.8948 | 0.9035 |
| BiT-M ResNet-50 (ImageNet-21k), evaluated at 448 px | 0.8975 | 0.9095 |
| **Final model (average)** | **0.9075** | **0.9148** |

Other results of the final model:

- Training accuracy without augmentation: 0.947 on HAM10000 and 0.940 on all sources.
- Test malignant recall: 0.645 (melanoma 0.479). Test ECE: 0.026.
- New lesions: 0.926 validation / 0.943 test.
- Lesions also seen in training: 0.875 validation / 0.861 test.

For new patients, a lesion-level split is the more honest estimate. An earlier single 7-class ResNet-50
run with that split reached 0.8613 validation and 0.8595 test accuracy.

### Software

| Environment | Use | Main packages |
|-------------|-----|---------------|
| `dev-metal` (recommended on Apple silicon) | training on the Apple GPU | Python 3.12, TensorFlow 2.18.1 + `tensorflow-metal` 1.2.0, Keras 3.15.1, NumPy 2.0.2, pandas 3.1, scikit-learn 1.9, matplotlib 3.11, seaborn 0.13, Pillow 13 |
| `dev` | CPU only | Python 3.12, TensorFlow 2.21, Keras 3.15 |

Only TensorFlow / Keras is used. PyTorch is not needed.

## Project layout

```
code/Group_8_Image_Recognition.ipynb   the only code file (deliverable)
data/                                  datasets, downloaded by hand (git-ignored)
outputs/                               resized images, weights, histories, figures (git-ignored)
final_outcome/                         frozen copy of the final executed notebook (git-ignored)
scripts/check-config.sh                checks the project rules in AGENTS.md
AGENTS.md, CLAUDE.md                   rules for the AI agents working on this project
```

## How to run

### 1. Set up the environment (once)

For an Apple-silicon Mac with GPU training:

```bash
conda create -n dev-metal python=3.12
```

```bash
conda activate dev-metal
```

```bash
pip install tensorflow==2.18.1 tensorflow-metal==1.2.0 keras==3.15.1 numpy==2.0.2 pandas scikit-learn matplotlib seaborn pillow jupyter ipykernel
```

```bash
python -m ipykernel install --user --name dev-metal --display-name "Python 3.12 (dev-metal, GPU)"
```

On other machines, install `tensorflow` without `tensorflow-metal`. TensorFlow 2.18 needs NumPy below 2.1.

### 2. Download the data (once)

Put the three datasets under `data/` with these folder names. The notebook searches sub-folders by
itself, so the inner layout does not matter.

| Folder | Content | Source |
|--------|---------|--------|
| `data/ISIC 2018/` | `HAM10000_metadata.csv` + 10,015 jpg images | [Kaggle: kmader/skin-cancer-mnist-ham10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000) |
| `data/ISIC 2019/` | `ISIC_2019_Training_GroundTruth.csv`, `ISIC_2019_Training_Metadata.csv` + 25,331 jpg images | [Kaggle: andrewmvd/isic-2019](https://www.kaggle.com/datasets/andrewmvd/isic-2019) |
| `data/BCN20000/` | `ISIC_2019_Test_GroundTruth.csv`, `ISIC_2019_Test_Metadata.csv` + `ISIC_2019_Test_Input/` (8,238 jpg images, or the zip) | [ISIC Challenge 2019 data](https://challenge.isic-archive.com/data/#2019) (CC BY-NC 4.0) |

If a metadata CSV is missing, age, sex and body site are treated as unknown.

### 3. Run the notebook

Start Jupyter from the project folder:

```bash
jupyter notebook code/Group_8_Image_Recognition.ipynb
```

Then select the kernel `Python 3.12 (dev-metal, GPU)` and use **Run All**.

- **First run:** the notebook resizes every image once into `outputs/resized_448/` and `outputs/resized_384/`.
  It also downloads the ImageNet and BiT weights, which needs Internet once.
- **Run time on an Apple M4 GPU:** about 7.5 hours for the ResNet-50 and about 6 hours for the BiT-M
  ResNet-50. A CPU is several times slower.
- **Stopping and resuming:** finished stages are skipped. If the kernel stops, run all cells again and
  training continues from the last saved epoch.
- **Re-running for results only:** if `outputs/run_448px_binary/model/` and `outputs/run_bit_384px_binary/model/`
  already hold the trained weights, *Run All* skips training and only evaluates.
- **Where the results go:** figures and tables are written to `outputs/run_448px_binary/`, and the BiT model
  to `outputs/run_bit_384px_binary/`.

### Running on Kaggle (optional)

1. Import the notebook.
2. Add the input datasets `kmader/skin-cancer-mnist-ham10000`, `andrewmvd/isic-2019` and
   `hillzhangjunyi/group8-bcn20000`.
3. Choose a GPU accelerator and turn the Internet on.
4. Use *Save & Run All (Commit)*.

The notebook detects Kaggle by itself and writes to `/kaggle/working/outputs`.

### Quick check (smoke test)

A few-minute run with 8 images per class per split and 1 epoch per stage. The results are written to a
separate folder.

```bash
jupyter nbconvert --to script code/Group_8_Image_Recognition.ipynb --output-dir /tmp/g8_smoke
```

```bash
cd code && G8_SMOKE=1 G8_OUT_DIR=/tmp/g8_smoke/out conda run -n dev-metal python /tmp/g8_smoke/Group_8_Image_Recognition.py
```

Use a new `G8_OUT_DIR` each time. Otherwise old checkpoints make the training cells skip.
