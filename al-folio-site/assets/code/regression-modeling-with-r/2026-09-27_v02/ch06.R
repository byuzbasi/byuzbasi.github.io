# Chapter 6. Categorical Predictors, Interactions, and Transformations
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 280 =====
tg <- datasets::ToothGrowth
tg <- transform(
  tg,
  supp = factor(supp, levels = c("VC", "OJ")),
  dose_factor = factor(dose, levels = c(0.5, 1, 2)),
  u = dose - 1
)
stopifnot(nrow(tg) == 60L, !anyNA(tg),
          identical(levels(tg$supp), c("VC", "OJ")))
cell_counts <- with(tg, table(supp, dose_factor))
cell_means <- with(
  tg, tapply(len, list(supp, dose_factor), mean)
)
stopifnot(all(cell_counts == 10L))
cell_counts
round(cell_means, 2)

# ===== Book block 2; source line 303 =====
group_col <- c(VC = "#1B4965", OJ = "#C65D21")
tg$offset <- ave(
  tg$len, tg$supp, tg$dose_factor,
  FUN = function(z) seq(-0.055, 0.055,
                        length.out = length(z))
)
plot(tg$dose + tg$offset, tg$len,
     col = group_col[tg$supp],
     pch = ifelse(tg$supp == "VC", 1, 16),
     xlab = "Recorded dose (mg/day)",
     ylab = "Recorded tooth length",
     xlim = c(0.38, 2.12))
for (g in levels(tg$supp)) {
  lines(c(0.5, 1, 2), cell_means[g, ],
        col = group_col[g], lwd = 2)
  points(c(0.5, 1, 2), cell_means[g, ],
         col = group_col[g], pch = 18, cex = 1.2)
}
legend("bottomright", levels(tg$supp), col = group_col,
       pch = c(1, 16), lwd = 2, bty = "n")

# ===== Book block 3; source line 330 =====
fit_treatment <- lm(len ~ dose_factor * supp, data = tg,
                    na.action = na.fail)
tg_sum <- tg
contrasts(tg_sum$dose_factor) <- contr.sum(3)
contrasts(tg_sum$supp) <- contr.sum(2)
fit_sum <- lm(len ~ dose_factor * supp, data = tg_sum,
              na.action = na.fail)
X_treatment <- model.matrix(fit_treatment)
X_sum <- model.matrix(fit_sum)
coding_check <- c(
  treatment_rank = qr(X_treatment)$rank,
  sum_rank = qr(X_sum)$rank,
  columns_each = ncol(X_treatment),
  max_fitted_difference = max(abs(
    fitted(fit_treatment) - fitted(fit_sum)
  )),
  max_residual_difference = max(abs(
    residuals(fit_treatment) - residuals(fit_sum)
  ))
)
coding_check
head(X_treatment, 3)
head(X_sum, 3)

# ===== Book block 4; source line 360 =====
fit_additive <- lm(
  len ~ u + supp, data = tg, na.action = na.fail
)
fit_interaction <- lm(
  len ~ u * supp, data = tg, na.action = na.fail
)
b <- coef(fit_interaction)
group_lines <- rbind(
  VC = c(intercept_at_dose_1 = b["(Intercept)"], slope = b["u"]),
  OJ = c(intercept_at_dose_1 = b["(Intercept)"] + b["suppOJ"],
         slope = b["u"] + b["u:suppOJ"])
)
grid <- expand.grid(dose = c(0.5, 1, 2), supp = levels(tg$supp))
grid$u <- grid$dose - 1
grid$fitted <- predict(fit_interaction, newdata = grid)
grid$OJ_minus_VC <- with(grid,
  ifelse(supp == "OJ",
         b["suppOJ"] + b["u:suppOJ"] * u,
         NA_real_))
round(coef(fit_additive), 4)
round(coef(fit_interaction), 4)
round(group_lines, 4)
transform(grid, fitted = round(fitted, 3),
          OJ_minus_VC = round(OJ_minus_VC, 3))

# ===== Book block 5; source line 391 =====
fits <- list(
  numeric_additive = fit_additive,
  numeric_interaction = fit_interaction,
  factor_interaction = fit_treatment,
  log2_interaction = lm(len ~ log2(dose) * supp, data = tg,
                        na.action = na.fail)
)
fit_account <- data.frame(
  representation = names(fits),
  model_columns = vapply(
    fits, function(m) ncol(model.matrix(m)), integer(1)
  ),
  residual_df = vapply(fits, df.residual, integer(1)),
  training_SSE = vapply(fits, deviance, numeric(1))
)
fit_account$training_SSE <- round(fit_account$training_SSE, 3)
fit_account
observed_grid <- expand.grid(dose = c(0.5, 1, 2),
                             supp = levels(tg$supp))
prediction_grid <- observed_grid
prediction_grid$u <- prediction_grid$dose - 1
prediction_grid$dose_factor <- factor(prediction_grid$dose,
  levels = levels(tg$dose_factor)
)
prediction_table <- cbind(
  observed_grid,
  sapply(fits, predict, newdata = prediction_grid)
)
transform(prediction_table,
  across_models_range = apply(
    prediction_table[, -(1:2)], 1,
    function(z) round(diff(range(z)), 3)
  )
)
