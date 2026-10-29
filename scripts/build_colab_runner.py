#!/usr/bin/env python3
"""Build code/Group_8_Image_Recognition_colab.ipynb, the Google Colab GPU run notebook.

Same idea as scripts/build_local_runner.py: the delivered notebook stays the single source of truth,
its cells are copied in order and a few "Colab run settings" cells are inserted. The only recipe
difference is the size of the seed ensemble (five instead of three), which a GPU makes affordable.

  python3 scripts/build_colab_runner.py          # write the Colab notebook
  python3 scripts/build_colab_runner.py --check  # exit 1 if the committed copy is stale

The settings cell also reads the G8_* variables of the local builder, so the Colab copy can be
smoke-tested on the local CPU before it is uploaded (outside Colab it writes to G8_RUN_ROOT).
"""
import json
import sys
from pathlib import Path

from build_local_runner import (ANCHOR_CONFIG, ANCHOR_MERGE, ANCHOR_PLAN, METADATA, ROOT,
                                SETTINGS_SMOKE, clean_cell, code_cell, find, markdown_cell,
                                read_notebook, split_training_cell)

TARGET = ROOT / "code" / "Group_8_Image_Recognition_colab.ipynb"
# Colab reads these keys and asks for a T4 GPU runtime when the notebook is opened.
COLAB_METADATA = {**METADATA, "accelerator": "GPU",
                  "colab": {"gpuType": "T4", "provenance": []}}

HEADER_MARKDOWN = """# Group 8 - Google Colab GPU run (resumable, five-seed ensemble)

Generated from `code/Group_8_Image_Recognition.ipynb` by `scripts/build_colab_runner.py`. The code
cells are identical and in the same order as the delivered notebook; four extra cells configure the
Colab run:

1. **Drive token**, first code cell: mounts Drive and reuses `MyDrive/Group_8/kaggle.json`, so a
   resumed session downloads the datasets without asking for the token again.
2. **Colab run settings**, right after the runtime cell: output folder and seed list.
3. **Smoke subset**, right before the `tf.data` pipelines: only used for a local wiring test.
4. **Epoch plan override**, in the middle of the training cell: records the seed list in the config.

The training recipe is the delivered one (25 epochs per seed). The only change is the ensemble: five
seeds instead of three, because a T4 trains one seed in about 1.5 hours instead of 9 on the CPU.

## How to run

1. Upload this notebook to Colab (`File -> Upload notebook`), or open it from Drive.
2. `Runtime -> Change runtime type -> T4 GPU` (the notebook already asks for one).
3. Optional, once: put your `kaggle.json` in `MyDrive/Group_8/`. Without it, Section 0 asks you to
   upload the token in every new session.
4. `Runtime -> Run all`. The first session downloads about 6 GB from Kaggle into `/content/data`.

Artifacts go to `MyDrive/Group_8/outputs_colab`, a fresh folder, so an older Colab run in
`MyDrive/Group_8/outputs` cannot be resumed by mistake.

## Time and interruptions

About 1.5 hours per seed on a T4, so about 8 hours for five seeds plus about 30 minutes for the
evaluation sections; that is more than one free session. A checkpoint is written to Drive after every
epoch, so when the session ends, reconnect and `Run all` again: each seed resumes from its last epoch
and finished seeds are skipped. To stop at fewer seeds, shorten `SEEDS` in the settings cell.
"""

SETTINGS_TOKEN = '''# Drive token - reuse MyDrive/Group_8/kaggle.json so a resumed session needs no token upload.
import sys, shutil
from pathlib import Path
if "google.colab" in sys.modules:
    from google.colab import drive
    drive.mount("/content/drive")
    saved_token = Path("/content/drive/MyDrive/Group_8/kaggle.json")
    if saved_token.is_file() and not Path("/content/kaggle.json").is_file():
        shutil.copy2(saved_token, "/content/kaggle.json")
    print("kaggle.json from Drive:", saved_token.is_file())'''

SETTINGS_RUNTIME = '''# Colab run settings - the delivered recipe with a five-seed ensemble, artifacts in a fresh folder.
SEEDS = [8, 42, 2026, 7, 1234]                # shorten this list to stop at fewer seeds
CHECKPOINT_EVERY_OVERRIDE = 1                 # a GPU epoch is cheap to replay, a lost session is not
if IN_COLAB:
    OUT_DIR = Path("/content/drive/MyDrive/Group_8/outputs_colab")
else:                                         # local wiring test only, see scripts/build_colab_runner.py
    run_root = Path(os.environ.get("G8_RUN_ROOT", "outputs/colab_run"))
    OUT_DIR = (run_root if run_root.is_absolute() else Path.cwd() / run_root).resolve()
    SEEDS = [int(value) for value in os.environ.get("G8_SEEDS", ",".join(map(str, SEEDS))).split(",")]
SMOKE = os.environ.get("G8_SMOKE") == "1"
STAGE_EPOCHS_OVERRIDE = os.environ.get("G8_STAGE_EPOCHS")
FIGURES, TABLES = OUT_DIR / "figures", OUT_DIR / "tables"
for folder in (FIGURES, TABLES, OUT_DIR / "model"):
    folder.mkdir(parents=True, exist_ok=True)
print("Colab run root:", OUT_DIR)
print("seeds:", SEEDS, "| checkpoint every", CHECKPOINT_EVERY_OVERRIDE, "epoch")'''

SETTINGS_PLAN = '''# Epoch plan override - records this run's seed list in the experiment config.
if STAGE_EPOCHS_OVERRIDE is not None:
    STAGE_EPOCHS = dict(zip(("A", "B", "C"), (int(value) for value in STAGE_EPOCHS_OVERRIDE.split(","))))
    TOTAL_EPOCHS = sum(STAGE_EPOCHS.values())
CHECKPOINT_EVERY = CHECKPOINT_EVERY_OVERRIDE
recorded = json.loads((TABLES / "experiment_config.json").read_text())
recorded.update(epochs_per_seed=TOTAL_EPOCHS, stages=dict(STAGE_EPOCHS), seeds=SEEDS)
recorded["selection"] = recorded["selection"].replace("the three models", f"the {len(SEEDS)} models")
recorded["predictions"] = recorded["predictions"].replace("the three seeds", f"the {len(SEEDS)} seeds")
(TABLES / "experiment_config.json").write_text(json.dumps(recorded, indent=2))
print(f"plan: {STAGE_EPOCHS} = {TOTAL_EPOCHS} epochs per seed, seeds {SEEDS}, "
      f"checkpoint every {CHECKPOINT_EVERY} epoch(s)")'''


def build():
    """Assemble the Colab notebook: header, token cell, the delivered cells, three settings cells."""
    notebook = read_notebook()
    cells = [clean_cell(cell) for cell in notebook["cells"]]
    config_cell = find(cells, ANCHOR_CONFIG)
    merge_cell = find(cells, ANCHOR_MERGE)
    plan_cell = find(cells, ANCHOR_PLAN)

    built = [markdown_cell("colab-run-header", HEADER_MARKDOWN)]
    for index, cell in enumerate(cells):
        if index == config_cell:
            built.append(code_cell("colab-run-token", SETTINGS_TOKEN))
        if index == plan_cell:
            head, tail = split_training_cell(cell)
            built += [head, code_cell("colab-run-plan", SETTINGS_PLAN), tail]
        else:
            built.append(cell)
        if index == config_cell:
            built.append(code_cell("colab-run-settings", SETTINGS_RUNTIME))
        if index == merge_cell:
            built.append(code_cell("colab-run-smoke", SETTINGS_SMOKE))

    return {"cells": built, "metadata": COLAB_METADATA, "nbformat": 4, "nbformat_minor": 5}


def main():
    """Write the Colab notebook, or verify with --check that the committed copy is current."""
    generated = build()
    if "--check" in sys.argv:
        current = json.loads(TARGET.read_text()) if TARGET.is_file() else None
        if current != generated:
            print(f"FAIL: {TARGET.relative_to(ROOT)} is stale, run: python3 scripts/build_colab_runner.py")
            return 1
        print(f"PASS: {TARGET.relative_to(ROOT)} matches the delivered notebook")
        return 0
    TARGET.write_text(json.dumps(generated, indent=1) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(generated['cells'])} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
