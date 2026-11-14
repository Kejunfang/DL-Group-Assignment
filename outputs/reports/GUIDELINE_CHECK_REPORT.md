> **2026-11-14:** the submission folder `final_outcome/` was renamed to `final_submission/`; paths written as `final_outcome/...` in this report refer to that folder under its old name.

# Guideline and Content Check Report - Group 8 (Bravo 8)

Date: 7 November 2026
Checked against: the assignment guideline PDF (B), the live requirements document (A), `README.md`, the final report (`Group_8_Image_Recognition.pdf/.docx`), the executed notebook in `final_outcome/` (the group's code standard) and the run artefacts in `outputs/`.

## 1. Report against the submission requirements

The group's original front matter is kept: page 1 is the cover with the project title, course header, due date, student declaration and typed signatures; page 2 is the contribution table; page 3 is the table of contents.

| Requirement | Evidence | Status |
|---|---|---|
| Single PDF report, file name `Group_8_Image_Recognition.pdf` | 35-page PDF in `outputs/report_final/` | PASS |
| Page limit 10-35 | 35 pages | PASS (at the upper limit) |
| Times New Roman 12 pt, 1.5 line spacing, justified body text | all Body and List Bullet paragraphs; audit found 0 explicit font or size violations | PASS |
| Title page: project title, member names/IDs, date | page 1: project title added above the declaration; all 5 names/IDs in the declaration table; due date displayed | PASS |
| Student declaration and signatures | page 1; 5 typed signatures | PRESENT (typed; handwritten if required) |
| Contribution table: group no., leader, tasks, percentage | page 2; 5 x 20% = 100% | PASS |
| Section on each member's role and contribution | Table of Contribution lists every role and percentage | PASS (table form) |
| Part 1, questions 1.1-1.4 | 1.1 VGG/chain rule + Figure 1; 1.2 ResNet/shortcuts + Table 1; 1.3 Inception multi-scale + Table 2; 1.4 CE vs MSE + backbone defence + Tables 3-4 | PASS |
| Part 2, items 2.1-2.20 | sections 2.1-2.20, each mapped to the guideline item | PASS |
| IEEE-style references | [1]-[29], every entry cited in the text | PASS |
| Single .ipynb code file with comments/explanations | `final_outcome/Group_8_Image_Recognition_final_executed.ipynb`, 39 outputs after the 2.15 refresh | PASS |
| Code file name `Group_8_Image_Recognition.ipynb` | `final_outcome/Group_8_Image_Recognition.ipynb` | PASS |
| 10-minute presentation (2 marks) | handled separately by the group; not in `final_outcome` | N/A for this folder |

## 2. Code against the coding requirements and Part 2 coverage

The group's code standard is the executed notebook `final_outcome/Group_8_Image_Recognition.ipynb`. Its 2.15 cell is self-contained: it reads the saved `test_predictions.csv`, so it can be run alone in a fresh kernel without re-running training or evaluation. Only the 2.15 cells were changed and the cell was run; its two-panel output is saved. All other cells and outputs are untouched.

| Item | Evidence in the executed notebook | Status |
|---|---|---|
| 2.1 libraries | printed TF/Keras versions; markdown library table | PASS |
| 2.2 forward pass / GradientTape | `w`, `x`, `y = w*x**2+1`, `tape.gradient`, explanation | PASS |
| 2.3 training vs evaluation memory | markdown + Dropout `training=True/False` demo | PASS |
| 2.4 preprocessing, label encoding, split | dataset loading, metadata, resize cache, tf.data, one-hot labels, leakage print | PASS |
| 2.5 batch through pipeline + two augmentations | batch shapes/pixels/metadata/label + 4-panel augmentation figure | PASS |
| 2.6 augmentation variance without label change | markdown explanation | PASS |
| 2.7 model building + summary() | two-input ResNet-50 model, `model.summary()`, stage parameter counts | PASS |
| 2.8 feature maps | `conv2_block3_out`, 16-channel grid | PASS |
| 2.9 spatial shrink / channel growth / backprop | markdown explanation + stage-shape table | PASS |
| 2.10 adaptive optimizer training | two-stage Adam training, fixed 12 epochs, checkpointing | PASS |
| 2.11 dual-axis loss + learning rate | two-panel loss/accuracy/LR figure | PASS |
| 2.12 optimizer principles and moments | markdown with first/second moments, bias correction, weight decay | PASS |
| 2.13 curve analysis | printed best/lowest-loss epochs, overfitting/underfitting text | PASS |
| 2.14 test accuracy/loss | `final_model.evaluate`, classification report, per-diagnosis and leakage tables | PASS |
| 2.15 normalized confusion matrix | updated to two panels: raw counts + normalized matrix; cell has been run and its output saved | PASS |
| 2.16 top-3 confident mistakes | sorted wrong predictions + 3-image figure | PASS |
| 2.17 error analysis | markdown analysis of the three images and confusion matrix | PASS |
| 2.18 unseen image + horizontal bar chart | random test image, softmax bar chart | PASS |
| 2.19 logits to softmax | markdown formula + hand calculation and comparison | PASS |
| 2.20 overconfidence and calibration | markdown + reliability diagram + ECE | PASS |
| Runs top-to-bottom with outputs | 41 outputs, no error outputs; the 2.15 cell output is saved | PASS |

Minor documentation issues in the executed notebook (do not affect code execution):
- Cell 36 says the single-model attempts were "all between 89 and 90%", but ResNet-152 (85.6%) and InceptionV3 (83.6%) were lower; the claim should be narrowed to the 448 px binary runs.
- Cell 11 comment says "stratified by class", while the code stratifies by `diagnosis` (the report is correct).
- These can be fixed in a working copy; the executed notebook is the frozen standard.

## 3. Content verification against the run artefacts

Key report numbers were recomputed or cross-checked:

- `outputs/run_448px_binary/summary.csv`: final val 0.9075, test 0.9148, test loss 0.2021, ECE 0.0259, training accuracy 0.947/0.940. All match the report.
- `test_predictions.csv`: test confusion 1,186 / 24 / 104 / 189; top-3 wrong images ISIC_0033300, ISIC_0033452, ISIC_0033154 with probabilities 0.9933 / 0.9883 / 0.9857; ISIC_0034059 predicted Malignant at 0.9554. All match.
- Executed notebook: ResNet member 0.9035, BiT member 0.9095, BiT validation 0.8975 at 448 px and 0.9048 at 384 px; ensemble 0.9075/0.9148; parameter counts 4,118 / 23,587,712 / 23,485,590; learning-curve values 0.2593, 0.2704, 0.2959, 0.2390, train 0.8987, val 0.8948; BiT 0.9551/0.9048; reliability bins and ECE. All match.
- Dataset counts recomputed from the CSVs: HAM10000 10,015 images / 7,470 lesions; ISIC 2019 15,316 after removing HAM duplicates; BCN20000 6,191 labelled images; SCC 596; training set 28,517 = 16,922 benign + 11,595 malignant (40.7%); split 7,010 / 1,502 / 1,503; leakage 551/1,502 (36.7%) and 512/1,503 (34.1%); multi-image melanoma share 19.6% vs 11.1% overall. All match.
- Metadata for ISIC_0033892 (NV) and ISIC_0034059 (MEL, age 70, male, upper extremity) matches the report.
- The macro and weighted-average rows added to the classification-report table are consistent with the test predictions (macro P/R/F1 0.903/0.813/0.848; weighted 0.913/0.915/0.909).

## 4. Corrections made during this check

- Added the project title above the declaration on page 1, keeping the group's cover/declaration layout.
- Corrected the He-initialisation explanation in 1.1.2 (2/n sets the variance factor to 1; it is not the cause of exploding gradients).
- Corrected 1.4.4: the lesion-level split reached about 86% validation accuracy, short of the 90% target (the earlier text said "below 86%").
- Added the missing ISIC 2019 citation [16] in 1.4.3; clarified "test error" in 1.2.5; changed the Table 6 label to HAM10000 so the Part 2 dataset cannot be confused with the "Not Use" ISIC 2018 Kaggle dataset; fixed the declaration spelling to "recognise".
- Refreshed the table-of-contents page numbers after the edits.
- Patched only the 2.15 markdown and code cells of the executed notebook to the two-panel confusion matrix; all other cells, outputs and execution counts are untouched. A backup is stored as `final_outcome/Group_8_Image_Recognition_final_executed_before_2p15.ipynb`.

## 5. Remaining risks / actions before submission

1. **Submission files:** the folder now contains exactly `Group_8_Image_Recognition.pdf` and `Group_8_Image_Recognition.ipynb`; use those two files.
2. **Google Doc:** the report writing doc (C) still contains the old 1.3/1.4 paste and old numbering; sync it with this DOCX or submit the PDF directly.
3. **Signatures:** the declaration contains typed names; use handwritten signatures if the school requires them.
4. **Page limit:** the report is exactly 35 pages, so avoid adding material without removing something.
5. **Figure 1 provenance:** it was redrawn from the values stated in the text after the original low-resolution figure was replaced; if the group still has the original 20-seed simulation output, put it back for research traceability.

## Verdict

The submission folder `final_outcome/` now contains exactly the required PDF and notebook with the correct names. The report meets the formatting, page-limit, title-page, declaration, contribution, Part 1/Part 2 and IEEE-reference requirements; the notebook has 41 outputs, no error outputs, and covers every coding item including the refreshed two-panel 2.15 cell. Presentation and the Google Doc are handled outside this folder.
