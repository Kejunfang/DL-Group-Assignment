> **Status: superseded by `GUIDELINE_CHECK_REPORT.md` (7 November 2026).** This earlier file records the format/humanization pass; the newer file is the current full guideline and content check.

# Format Check, Unification and Humanization Report - Group 8 (Bravo 8)

Date: 7 November 2026
Scope: CSC60904/CSC62904 Deep Learning Group Assignment (30%)
Deliverables: `Group_8_Image_Recognition.docx`, `Group_8_Image_Recognition.pdf` (35 pages)
Backups: `Group_8_Image_Recognition_before_humanize.docx` / `.pdf`

## 1. Problems found in the merged draft

1. Two layouts in one document: Part 1 was single-spaced and left-aligned, Part 2 was 1.5-spaced and justified.
2. Sections 1.3 and 1.4 were raw pastes: missing heading levels and numbers, a figure placeholder still read `/home/claude/fig/fig3_inception.png`, Figure 1 and 2 captions were duplicated, citations were author-year.
3. Figure and table numbers collided: Part 1 used Figures 1-4 and Tables 1-4 while Part 2 restarted at Figures 3-11 and Tables 2-13.
4. Captions and tables were inconsistent: caption position varied, some table cells used Cardo, table widths varied.
5. Two reference systems: IEEE [1]-[20] plus an extra APA list; citations in 1.3/1.4 pointed to the wrong entries.
6. Front matter gaps: no project title/members/date on the title page, no 1.3/1.4 entries in the contents, stale page numbers, "Table of Content".
7. Equation formatting: Part 1 equations were plain text with lost superscripts, Part 2 equations were unnumbered, the Adam square root was lost.
8. Typography mix: "Normalized" vs "normalised", literal " x " dimensions, "1e-3", "Eq."/"Equivalent", hyphen ranges.

## 2. Format work completed

- One A4 document, Times New Roman 12 pt, 1.5 line spacing, justified body text, 1.8 cm margins, 35 pages.
- Heading numbering unified: 1.1.1-1.4.4, 2.1-2.20, 2.13.1.
- Missing 1.3/1.4 written into report form; all citations converted to IEEE.
- Reference list extended to [1]-[29]; duplicate APA list removed; all entries cited.
- Figures 1-13 and Tables 1-16 renumbered sequentially, in-text references updated; table captions above tables, figure captions below figures.
- Figures 1-4 regenerated at 300-400 dpi; confusion-matrix figure rebuilt with consistent spelling.
- Display equations (1)-(22) rebuilt as native Word equations; inline maths restored.
- Title page, declaration table, contribution table and static table of contents with verified page numbers added.
- Table style unified: Times New Roman 10 pt, bold shaded header, borders, no split rows, repeated header.
- British spelling, x multiplication sign, en-dash ranges, 10^-n notation and ±90 degrees unified.

## 3. Humanization pass (after the group filled in signatures and contribution percentages)

- The group's edited DOCX was used as the base, so the filled contribution percentages (20% each), typed signatures, added table rows and adjusted table sizes are preserved unchanged.
- All 129 body prose paragraphs in Part 1 and Part 2 were rewritten following the humanizer skill: 9,420 words before, 9,350 after.
- Removed AI-writing patterns: "not X but Y" contrasts, one-line closers, forced triads, staged signposting, empty emphasis, inflated wording and em dashes. Sentences were split or merged within paragraphs, and openings were varied.
- A programmatic check confirmed that every number, percentage, `[n]` citation, `$...$` maths block and superscript/subscript token is unchanged; no paragraph was merged or split.
- Tables, figures, equations, captions, references, the declaration and the technical appendix keep their factual wording; only report prose was rewritten.
- The contribution table's first column was widened so "No." no longer wraps, and margins were reduced from 1.9 cm to 1.8 cm to keep the document within the 35-page limit after the group's table edits.
- The table of contents page numbers were recomputed from the final PDF and verified against the rendered pages.

## 4. Compliance check

| Requirement | Status |
|---|---|
| Times New Roman, 12 pt, 1.5 line spacing, justified | PASS |
| Page limit 10-35 pages | PASS - 35 pages |
| Title page with project title, member names/IDs, date | PASS |
| Student declaration and contribution table | PASS - signatures and 20% contributions filled |
| Part 1: questions 1.1-1.4 | PASS |
| Part 2: items 2.1-2.20 | PASS |
| IEEE-style references | PASS - [1]-[29], all cited |
| Single PDF report + single notebook | PDF ready; notebook unchanged |

## 5. Remaining action

The Google Doc still contains the old 1.3/1.4 paste and old numbering. Replace its content with this DOCX, or submit this PDF directly.

Result values were not modified: final ensemble validation 0.9075, test 0.9148.
