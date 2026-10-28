#!/usr/bin/env bash
# Launch the local CPU backup run (code/Group_8_Image_Recognition_local.ipynb) in the background.
#
#   bash scripts/run-local.sh                    # full plan, seeds 8,42,2026, outputs/local_run
#   bash scripts/run-local.sh --smoke            # wiring test: 1 epoch per stage, a few images per class
#   bash scripts/run-local.sh outputs/my_run     # custom output folder
#
# The notebook is exported to a plain script with nbconvert first, so the same cells produce a live,
# unbuffered log instead of being trapped inside the saved .ipynb. The run is resumable: every epoch
# writes last.weights.h5 plus the history csv, so rerunning the same command continues where it
# stopped. caffeinate keeps the Mac awake for the whole run (-d display, -i idle, -m disk, -s system
# on AC power).
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
notebook="code/Group_8_Image_Recognition_local.ipynb"
run_root="$root/outputs/local_run"
smoke=0
for arg in "$@"; do
  case "$arg" in
    --smoke) smoke=1 ;;
    *) run_root="$arg" ;;
  esac
done

if [ "$smoke" = 1 ]; then
  [ "$run_root" = "$root/outputs/local_run" ] && run_root="$root/outputs/local_run_smoke"
  export G8_SMOKE=1 G8_STAGE_EPOCHS=1,1,1 G8_SEEDS=8
fi

mkdir -p "$run_root"
cd "$root"
export G8_RUN_ROOT="$run_root"
export G8_SEEDS="${G8_SEEDS:-8,42,2026}"

conda run --no-capture-output -n dev jupyter nbconvert --to script \
  --output-dir "$run_root" "$notebook" >/dev/null
script="$run_root/$(basename "${notebook%.ipynb}").py"

caffeinate -dimsu nohup conda run --no-capture-output -n dev python -u "$script" \
  >>"$run_root/run.log" 2>&1 &
echo "local run started (pid $!)"
echo "run root: $run_root"
echo "log:      $run_root/run.log"
echo "monitor:  tail -f '$run_root/run.log'"
