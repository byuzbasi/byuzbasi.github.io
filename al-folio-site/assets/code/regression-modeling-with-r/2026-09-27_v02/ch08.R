# Chapter 8. Generalization, Resampling, and Model Selection
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 106 =====
predictions <- data.frame(
  case = 1:4,
  reference_outcome = c(4, 8, 6, 10),
  prediction_a = c(5, 7, 7, 9),
  prediction_b = c(4, 8, 6, 13)
)
predictions$error_a <-
  predictions$reference_outcome - predictions$prediction_a
predictions$error_b <-
  predictions$reference_outcome - predictions$prediction_b
mean(predictions$error_b^2)
sqrt(mean(predictions$error_b^2))
mean(abs(predictions$error_b))

# ===== Book block 2; source line 288 =====
fold_scores <- data.frame(
  fold = 1:2,
  n = c(2L, 6L),
  sse = c(8, 6)
)
fold_scores$mse <- fold_scores$sse / fold_scores$n
fold_scores$rmse <- sqrt(fold_scores$mse)
fold_scores$observation_weight <-
  fold_scores$n / sum(fold_scores$n)
pooled_mse <- sum(fold_scores$sse) / sum(fold_scores$n)
sqrt(pooled_mse)
