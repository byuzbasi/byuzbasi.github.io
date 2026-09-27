# Reasoning Through Regression — chapter applications

**Author: Prof. Dr. Bahadır Yüzbaşı**  
**Revision: 27 September 2026 — verified worked examples**

Read the chapter explanation before running its code. The twelve `chNN.R` files contain the book's 48 R blocks in their original order. Comments identify each block and its manuscript line. `source_map.json` records the source mapping and SHA-256 hashes. These are worked applications; unseen instructor solutions are not included.

## Start a chapter

Unzip this entire folder, open a terminal in the folder, and run, for example:

```sh
Rscript --vanilla run_chapter.R 3 smoke results/ch03_attempt01
```

The third argument must name a new output directory. The runner refuses to overwrite an existing path, records the executed code, console output, session information, and SHA-256 manifest, and saves plots for Chapters 5 and 6. Change the output directory for a new attempt. There is no hidden package installation or download.

You can instead open `ch03.R` in RStudio and run its blocks from top to bottom in a fresh R session. This interactive route does not produce the runner's output manifest. In Chapter 7, print `values` after the calculation to inspect its table.

## Dependencies and input provenance

The wrapper requires `digest` for SHA-256 checksums. The chapter calculations use base/recommended R except for `MASS` in Chapter 11 and `MASS`, `glmnet`, `digest`, and `knitr` in Chapter 12. The validation record identifies tested versions. If a required package is missing, the wrapper stops and names it.

| Chapter | Application and prerequisites | Inputs |
|---|---|---|
| 1 | Mean, deviations and squared loss; numeric vectors | Four stipulated values |
| 2 | Least-squares line, identities and predictions; Chapter 1 | Four stipulated pairs |
| 3 | Multiple regression, residualization and joint support; Chapter 2 | Four stipulated triples |
| 4 | Covariance, t intervals and prediction intervals; Chapters 2–3 | The same teaching table |
| 5 | Residuals, leverage, deletion and Cook's distance; Chapters 3–4 | `datasets::anscombe` |
| 6 | Factors, interactions and coordinate changes; Chapters 3–5 | `datasets::ToothGrowth` |
| 7 | Coefficient disagreement and prediction agreement; Chapter 3 | Three stipulated predictor rows |
| 8 | Prediction loss and pooled fold scores; Chapters 1–4 | Four stipulated predictions; two supplied fold summaries |
| 9 | Ridge, directional MSE and separate assessment; Chapters 7–8 | One frozen synthetic realization; `datasets::longley` |
| 10 | Soft thresholding, coordinate descent, tuning and selection; Chapters 8–9 | Orthogonal hand example; frozen synthetic data; `datasets::mtcars` |
| 11 | Logistic probabilities, scores, calibration and thresholds; Chapters 4 and 8 | Stipulated example; one frozen realization; `MASS::birthwt` |
| 12 | Reproducible inference and prediction study; preceding chapters | `MASS::cpus`, 209 historical processor records |

Original data objects are not overwritten. Transformations, units, exclusions, factor levels, seeds and data roles are specified in the corresponding chapter and visible in the code. Chapter 12's UCI provenance record is [Computer Hardware](https://archive.ics.uci.edu/dataset/29/computer%2Bhardware), DOI 10.24432/C5830D, with CC BY 4.0 attribution. Other packaged data retain the provenance documented by R and MASS.

## Smoke versus complete execution

For Chapters 1–9 and 11, `smoke` runs all of the chapter's small worked-example blocks. For Chapters 10 and 12, it runs **only blocks 1–2**: Chapter 10's orthogonal calculation and coordinate-descent check, or Chapter 12's input and split validation. It does not certify later model fitting or resampling.

`complete` runs every block of the selected chapter. Chapter 10 includes repeated tuning within its selection ledger. The approved fold-local grid and observation-weighted score are now implemented. The author completed the revised full numerical run; all 28 units and their manifests passed validation. This workload is not started by smoke mode. A complete Chapter 12 report uses `ch12_complete_study.R`, an unchanged copy of the previously validated full-study script; the five book blocks illustrate its central computations. The full script requires one new output-directory argument and creates the study tables, diagnostic figures, software record and SHA-256 manifest. Its earlier completed results were verified without rerunning that workload in this revision.

## What to check

Compare the saved output with the chapter's worked values. For example, Chapter 1 has mean 7 and squared deviations summing to 20; Chapter 2 has intercept 3, slope 1.6 and SSE 7.2; Chapter 3 has coefficients `(11/3, 8/3, -4/3)` and SSE 4; Chapter 7's prediction differences are `(-0.2, -12, -0.4)`; Chapter 8's pooled MSE is 1.75. Floating-point roundoff is expected.

Execution success and arithmetic agreement support reproducibility for the checked example. They do not establish model adequacy, causality, future prediction accuracy or independent student understanding. Record your explanation and the help you used before consulting feedback.

## Verification and scope

The centered-error covariance and estimated-intercept explanations in Chapter 9, and the observation-weighted fold scores and fold-local penalty grids in Chapter 10, were corrected in this edition. The author completed the Chapter 10 numerical run; 28 CV/refit units, output dimensions, scientific signatures, SHA-256 manifests and KKT checks passed. The largest KKT residual was approximately 9.92e-9. The updated tables and Figure 10.2 match those verified outputs. Other chapter calculations retain their validated numerical definitions.

For the revised synthetic example, lasso selects x1, x3 and x5: development CV-RMSE 1.0789 and assessment RMSE 1.0313. Elastic net at alpha 0.5 selects six slopes: CV-RMSE 1.0919 and assessment RMSE 1.0642. The 12-subsample frequencies describe this finite procedure. These checks establish reproducibility of the worked examples; they do not establish general predictive superiority or classroom effectiveness.
