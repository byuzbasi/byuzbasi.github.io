# Chapter 12. A Complete Regression Study
# Reasoning Through Regression: Inference, Prediction, and Regularization with R
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 88 =====
required <- c("MASS", "glmnet", "digest", "knitr")
stopifnot(all(vapply(required, requireNamespace, logical(1), quietly = TRUE)))

raw_cpus <- MASS::cpus
raw_hash <- digest::digest(raw_cpus, algo = "sha256", serialize = TRUE)
stopifnot(nrow(raw_cpus) == 209L, ncol(raw_cpus) == 9L)
stopifnot(sum(is.na(raw_cpus)) == 0L)

analysis_data <- data.frame(
  row_id = seq_len(nrow(raw_cpus)),
  name = as.character(raw_cpus$name),
  perf = raw_cpus$perf,
  log_perf = log(raw_cpus$perf),
  log_syct = log(raw_cpus$syct),
  log_mmin = log(raw_cpus$mmin),
  log_mmax = log(raw_cpus$mmax),
  log1p_cach = log1p(raw_cpus$cach),
  log1p_chmin = log1p(raw_cpus$chmin),
  log1p_chmax = log1p(raw_cpus$chmax),
  stringsAsFactors = FALSE
)
predictor_names <- c(
  "log_syct", "log_mmin", "log_mmax",
  "log1p_cach", "log1p_chmin", "log1p_chmax"
)
stopifnot(identical(raw_cpus, MASS::cpus))
stopifnot(identical(raw_hash,
  digest::digest(MASS::cpus, algo = "sha256", serialize = TRUE)))

# ===== Book block 2; source line 135 =====
split_seed <- 20261201L
fold_seed <- 20261202L
set.seed(split_seed)
development_rows <- sort(sample(
  seq_len(nrow(analysis_data)),
  size = floor(0.75 * nrow(analysis_data)), replace = FALSE
))
assessment_rows <- setdiff(seq_len(nrow(analysis_data)), development_rows)

set.seed(fold_seed)
development_folds <- sample(rep(1:5, length.out = length(development_rows)))
stopifnot(length(development_rows) == 156L)
stopifnot(length(assessment_rows) == 53L)
stopifnot(all(table(development_folds) %in% c(31L, 32L)))

x_all <- as.matrix(analysis_data[, predictor_names])
y_all <- analysis_data$log_perf
x_development <- x_all[development_rows, , drop = FALSE]
y_development <- y_all[development_rows]
x_assessment <- x_all[assessment_rows, , drop = FALSE]

# ===== Book block 3; source line 332 =====
fit_scaler <- function(x) {
  center <- colMeans(x)
  scale <- sqrt(colMeans(sweep(x, 2, center, "-")^2))
  if (any(!is.finite(scale)) || any(scale <= 0)) stop("Invalid scale.")
  list(center = center, scale = scale)
}
apply_scaler <- function(x, s) {
  sweep(sweep(x, 2, s$center, "-"), 2, s$scale, "/")
}
penalty_grid <- function(z, y, alpha, points = 60L) {
  ref <- max(abs(drop(crossprod(z, y - mean(y))))) / nrow(z)
  if (alpha == 0) {
    ratio <- 10^seq(2, -4, length.out = points)
    lambda <- ref * ratio
  } else {
    ratio <- 10^seq(0, -4, length.out = points)
    lambda <- (ref / alpha) * ratio
  }
  list(lambda = lambda, ratio = ratio, reference = ref)
}
fit_path <- function(z, y, alpha, lambda) {
  glmnet::glmnet(
    z, y, family = "gaussian", alpha = alpha, lambda = lambda,
    intercept = TRUE, standardize = FALSE,
    control = list(thresh = 1e-10, maxit = 100000L)
  )
}
cv_penalized <- function(x, y, folds, alpha) {
  sse <- numeric(60); count <- 0L
  for (fold in sort(unique(folds))) {
    analysis <- folds != fold; validation <- !analysis
    scaler <- fit_scaler(x[analysis, , drop = FALSE])
    za <- apply_scaler(x[analysis, , drop = FALSE], scaler)
    zv <- apply_scaler(x[validation, , drop = FALSE], scaler)
    grid <- penalty_grid(za, y[analysis], alpha)
    path <- fit_path(za, y[analysis], alpha, grid$lambda)
    pred <- as.matrix(predict(path, zv, s = grid$lambda))
    err <- sweep(pred, 1, y[validation], "-")
    sse <- sse + colSums(err^2); count <- count + sum(validation)
  }
  rmse <- sqrt(sse / count)
  list(rmse = rmse, selected = which(rmse <= min(rmse) + 1e-12)[1])
}

simple_prediction <- matrix(NA_real_, nrow(x_development), 2,
  dimnames = list(NULL, c("baseline", "ols")))
for (fold in 1:5) {
  analysis <- development_folds != fold
  validation <- !analysis
  scaler <- fit_scaler(x_development[analysis, , drop = FALSE])
  za <- apply_scaler(x_development[analysis, , drop = FALSE], scaler)
  zv <- apply_scaler(x_development[validation, , drop = FALSE], scaler)
  simple_prediction[validation, "baseline"] <- mean(y_development[analysis])
  fit <- lm.fit(cbind(1, za), y_development[analysis])
  simple_prediction[validation, "ols"] <- cbind(1, zv) %*% fit$coefficients
}
alpha <- c(ridge = 0, elastic_net = 0.5, lasso = 1)
penalized_cv <- lapply(alpha, function(a)
  cv_penalized(x_development, y_development, development_folds, a))
cv_rmse <- c(
  baseline = sqrt(mean((y_development - simple_prediction[, 1])^2)),
  ols = sqrt(mean((y_development - simple_prediction[, 2])^2)),
  vapply(penalized_cv, function(x) x$rmse[x$selected], numeric(1))
)
round(cv_rmse, 6)

# ===== Book block 4; source line 443 =====
selected_index <- penalized_cv$ridge$selected
development_scaler <- fit_scaler(x_development)
z_development <- apply_scaler(x_development, development_scaler)
z_assessment <- apply_scaler(x_assessment, development_scaler)
final_grid <- penalty_grid(z_development, y_development, alpha = 0)
final_ridge <- fit_path(
  z_development, y_development, alpha = 0,
  lambda = final_grid$lambda
)
selected_lambda <- final_grid$lambda[selected_index]
ridge_prediction <- as.numeric(predict(
  final_ridge, z_assessment, s = selected_lambda, type = "response"
))

# The assessment response is opened only after the procedure is frozen.
y_assessment <- y_all[assessment_rows]
development_mean <- mean(y_development)
score <- function(observed, predicted, reference) c(
  rmse = sqrt(mean((observed - predicted)^2)),
  mae = mean(abs(observed - predicted)),
  r2 = 1 - sum((observed - predicted)^2) /
    sum((observed - reference)^2)
)
rbind(
  baseline = score(y_assessment,
    rep(development_mean, length(y_assessment)), development_mean),
  ridge = score(y_assessment, ridge_prediction, development_mean)
)

# ===== Book block 5; source line 535 =====
inference_data <- analysis_data[development_rows,
  c("log_perf", predictor_names)]
ols_fit <- lm(log_perf ~ log_syct + log_mmin + log_mmax +
  log1p_cach + log1p_chmin + log1p_chmax, data = inference_data)
ols_table <- coef(summary(ols_fit))
critical <- qt(0.975, df.residual(ols_fit))
ols_intervals <- cbind(
  estimate = ols_table[, "Estimate"],
  lower = ols_table[, "Estimate"] - critical * ols_table[, "Std. Error"],
  upper = ols_table[, "Estimate"] + critical * ols_table[, "Std. Error"]
)
manual_vif <- function(x) vapply(seq_len(ncol(x)), function(j) {
  fit <- lm.fit(cbind(1, x[, -j, drop = FALSE]), x[, j])
  r2 <- 1 - sum(fit$residuals^2) /
    sum((x[, j] - mean(x[, j]))^2)
  1 / (1 - r2)
}, numeric(1))
diagnostic_summary <- c(
  sigma = summary(ols_fit)$sigma,
  r_squared = summary(ols_fit)$r.squared,
  max_abs_standardized_residual = max(abs(rstandard(ols_fit))),
  max_leverage = max(hatvalues(ols_fit)),
  max_cook = max(cooks.distance(ols_fit))
)
round(diagnostic_summary, 6)
round(manual_vif(as.matrix(inference_data[, predictor_names])), 3)
