#!/usr/bin/env python3
"""Build code/Group_8_Image_Recognition_local.ipynb, the resumable CPU backup notebook.

The delivered notebook (code/Group_8_Image_Recognition.ipynb) stays the single source of truth:
this script copies its cells in order and inserts three "local run settings" cells, plus a short
markdown header. Nothing else changes, so the backup run cannot drift away from the deliverable.

  python3 scripts/build_local_runner.py          # write the local notebook
  python3 scripts/build_local_runner.py --check  # exit 1 if the committed copy is stale

The settings cells read the environment so the same notebook can be launched headless
(scripts/run-local.sh) or run interactively cell by cell:
  G8_RUN_ROOT      output folder (default outputs/local_run, so the notebook's outputs/ stays intact)
  G8_SEEDS         comma separated seed list (default 8,42,2026)
  G8_SMOKE         1 = a few images per class and one epoch per stage, to test the wiring in minutes
  G8_STAGE_EPOCHS  stage A,B,C epoch counts (default: the notebook's own plan)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "code" / "Group_8_Image_Recognition.ipynb"
TARGET = ROOT / "code" / "Group_8_Image_Recognition_local.ipynb"

HEADER_MARKDOWN = """# Group 8 - local CPU backup run (resumable)

Generated from `code/Group_8_Image_Recognition.ipynb` by `scripts/build_local_runner.py`. The code
cells are identical and in the same order as the delivered notebook, so this backup cannot drift
away from the submitted code. Three extra cells configure the local run:

1. **Local run settings**, right after the runtime cell: output folder, seed list, smoke switch,
   checkpoint frequency. Edit this cell (or set the `G8_*` environment variables) before running.
2. **Smoke subset**, right before the `tf.data` pipelines: a few images per class when `SMOKE` is on.
3. **Epoch plan override**, in the middle of the training cell: a shorter epoch plan, if wanted.

## How to run

* Interactive: activate the `dev` conda environment, open this notebook, `Run All`. The training
  cell loops over the seeds in order, and stages A, B and C run back to back.
* Headless, detached, logged (keeps the Mac awake):

      bash scripts/run-local.sh                 # full plan, seeds 8/42/2026, log in outputs/local_run
      bash scripts/run-local.sh --smoke         # wiring test: 1 epoch per stage, a few images per class
      bash scripts/run-local.sh outputs/my_run  # custom output folder

## Why it can be interrupted

Every epoch appends a row to `tables/train_history_seed<seed>.csv` and (with `CHECKPOINT_EVERY = 1`)
writes `model/seed<seed>/last.weights.h5`. The training cell reads the history back, truncates it to
the last saved checkpoint and resumes from the next epoch, so a sleep, a crash or a closed kernel
costs at most one epoch. Artifacts land in `outputs/local_run/`, never in the delivered `outputs/`.
"""

SETTINGS_RUNTIME = '''# Local run settings - the only cell that differs from the delivered notebook.
# Artifacts go to outputs/local_run so a multi-day CPU run never overwrites the notebook's outputs/.
RUN_ROOT = Path(os.environ.get("G8_RUN_ROOT", "outputs/local_run"))
RUN_SEEDS = [int(value) for value in os.environ.get("G8_SEEDS", "8,42,2026").split(",")]
SMOKE = os.environ.get("G8_SMOKE") == "1"     # True: a few images per class, 1 epoch per stage
STAGE_EPOCHS_OVERRIDE = os.environ.get("G8_STAGE_EPOCHS")   # e.g. "1,1,1"; None keeps the plan
CHECKPOINT_EVERY_OVERRIDE = 1                 # a CPU epoch is expensive: save weights after each one

OUT_DIR = (RUN_ROOT if RUN_ROOT.is_absolute() else Path.cwd() / RUN_ROOT).resolve()
FIGURES, TABLES = OUT_DIR / "figures", OUT_DIR / "tables"
for folder in (FIGURES, TABLES, OUT_DIR / "model"):
    folder.mkdir(parents=True, exist_ok=True)
SEEDS = list(RUN_SEEDS)
print("local run root:", OUT_DIR)
print("seeds:", SEEDS, "| smoke:", SMOKE, "| checkpoint every", CHECKPOINT_EVERY_OVERRIDE, "epoch(s)")'''

SETTINGS_SMOKE = '''# Smoke subset - only active when SMOKE is True, so the wiring test runs in minutes, not days.
if SMOKE:
    per_class_train, per_class_eval = 8, 4
    train_df = train_df.groupby("label", group_keys=False).head(per_class_train).reset_index(drop=True)
    val_df = val_df.groupby("label", group_keys=False).head(per_class_eval).reset_index(drop=True)
    test_df = test_df.groupby("label", group_keys=False).head(per_class_eval).reset_index(drop=True)
    external_df = external_df.groupby("label", group_keys=False).head(per_class_eval).reset_index(drop=True)
    expected_total = len(train_df)
    print(f"smoke subset: train {len(train_df)} | val {len(val_df)} | "
          f"test {len(test_df)} | external {len(external_df)}")'''

SETTINGS_PLAN = '''# Epoch plan override - only active when STAGE_EPOCHS_OVERRIDE is set (None keeps the notebook plan).
if STAGE_EPOCHS_OVERRIDE is not None:
    STAGE_EPOCHS = dict(zip(("A", "B", "C"), (int(value) for value in STAGE_EPOCHS_OVERRIDE.split(","))))
    TOTAL_EPOCHS = sum(STAGE_EPOCHS.values())
CHECKPOINT_EVERY = CHECKPOINT_EVERY_OVERRIDE
recorded = json.loads((TABLES / "experiment_config.json").read_text())
recorded.update(epochs_per_seed=TOTAL_EPOCHS, stages=dict(STAGE_EPOCHS), seeds=SEEDS)
(TABLES / "experiment_config.json").write_text(json.dumps(recorded, indent=2))
print(f"plan: {STAGE_EPOCHS} = {TOTAL_EPOCHS} epochs per seed, seeds {SEEDS}, "
      f"checkpoint every {CHECKPOINT_EVERY} epoch(s)")'''

ANCHOR_CONFIG = "# Section 0 - runtime, paths and seeds"
ANCHOR_MERGE = "# Merge the extra ISIC 2019 images"
ANCHOR_PLAN = "# 2.10 - Training plan"
SPLIT_AFTER = "CHECKPOINT_EVERY = 5"
ANCHOR_SEED_LOOP = "for seed in SEEDS:"
# Fixed kernel metadata: the delivered notebook is run in Jupyter, which rewrites its metadata and
# stores outputs. Neither belongs in a generated copy, so --check compares code and markdown only.
METADATA = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}}


def read_notebook():
    """The delivered notebook as a dict."""
    return json.loads(NOTEBOOK.read_text())


def source_of(cell):
    """Cell source as one string."""
    return "".join(cell["source"])


def find(cells, anchor):
    """Index of the single code cell whose source contains `anchor` (fails loudly when ambiguous)."""
    hits = [index for index, cell in enumerate(cells)
            if cell["cell_type"] == "code" and anchor in source_of(cell)]
    if len(hits) != 1:
        raise SystemExit(f"anchor {anchor!r} found in {len(hits)} code cells, expected exactly 1")
    return hits[0]


def markdown_cell(cell_id, text):
    """A markdown cell in nbformat 4.5 shape."""
    return {"cell_type": "markdown", "id": cell_id, "metadata": {},
            "source": text.splitlines(keepends=True)}


def code_cell(cell_id, text):
    """A code cell in nbformat 4.5 shape, ready to execute."""
    return {"cell_type": "code", "execution_count": None, "id": cell_id, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


def clean_cell(cell):
    """A delivered cell without the outputs and execution count a Jupyter run leaves behind."""
    if cell["cell_type"] != "code":
        return cell
    return {**cell, "execution_count": None, "outputs": []}


def split_training_cell(cell):
    """Split the training cell after CHECKPOINT_EVERY so the plan override runs before the loop."""
    lines = cell["source"]
    hit = [index for index, line in enumerate(lines) if line.startswith(SPLIT_AFTER)]
    if len(hit) != 1:
        raise SystemExit(f"expected exactly one line starting with {SPLIT_AFTER!r} in the training cell")
    head, tail = lines[:hit[0] + 1], lines[hit[0] + 1:]
    if sum(ANCHOR_SEED_LOOP in line for line in tail) != 1:
        raise SystemExit(f"expected exactly one {ANCHOR_SEED_LOOP!r} after {SPLIT_AFTER!r}")
    return {**cell, "source": head}, {**cell, "id": f"{cell['id']}-loop", "source": tail}


def build():
    """Assemble the local notebook: header markdown, the delivered cells, three settings cells."""
    notebook = read_notebook()
    cells = [clean_cell(cell) for cell in notebook["cells"]]
    config_cell = find(cells, ANCHOR_CONFIG)
    merge_cell = find(cells, ANCHOR_MERGE)
    plan_cell = find(cells, ANCHOR_PLAN)

    built = [markdown_cell("local-run-header", HEADER_MARKDOWN)]
    for index, cell in enumerate(cells):
        if index == plan_cell:
            head, tail = split_training_cell(cell)
            built += [head, code_cell("local-run-plan", SETTINGS_PLAN), tail]
        else:
            built.append(cell)
        if index == config_cell:
            built.append(code_cell("local-run-settings", SETTINGS_RUNTIME))
        if index == merge_cell:
            built.append(code_cell("local-run-smoke", SETTINGS_SMOKE))

    return {"cells": built, "metadata": METADATA, "nbformat": 4, "nbformat_minor": 5}


def main():
    """Write the local notebook, or verify with --check that the committed copy is current."""
    generated = build()
    if "--check" in sys.argv:
        current = json.loads(TARGET.read_text()) if TARGET.is_file() else None
        if current != generated:
            print(f"FAIL: {TARGET.relative_to(ROOT)} is stale, run: python3 scripts/build_local_runner.py")
            return 1
        print(f"PASS: {TARGET.relative_to(ROOT)} matches the delivered notebook")
        return 0
    TARGET.write_text(json.dumps(generated, indent=1) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(generated['cells'])} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
