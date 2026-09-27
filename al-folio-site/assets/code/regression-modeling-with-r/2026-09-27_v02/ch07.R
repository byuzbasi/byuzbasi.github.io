# Chapter 7. Multicollinearity and Unstable Estimates
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 366 =====
values <- data.frame(
  x1 = c(10, 10, 8),
  x2 = c(10.1, 16, 8.2)
)
values$prediction_a <- values$x1 + 4 * values$x2
values$prediction_b <- 3 * values$x1 + 2 * values$x2
values$difference <- values$prediction_b - values$prediction_a
values$identity_difference <- 2 * (values$x1 - values$x2)
