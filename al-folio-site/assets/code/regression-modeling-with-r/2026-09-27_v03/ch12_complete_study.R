#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) {
  stop(
    "Usage: Rscript ch12_complete_regression_study.R OUTPUT_DIRECTORY",
    call. = FALSE
  )
}

output_directory <- args[[1L]]
if (dir.exists(output_directory) || file.exists(output_directory)) {
  stop("Refusing to overwrite output path: ", output_directory, call. = FALSE)
}
dir.create(output_directory, recursive = TRUE, showWarnings = FALSE)
if (!dir.exists(output_directory)) {
  stop("Could not create output directory: ", output_directory, call. = FALSE)
}

required_packages <- c("MASS", "glmnet", "digest", "knitr")
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_packages)) {
  stop(
    "Missing required package(s): ",
    paste(missing_packages, collapse = ", "),
    call. = FALSE
  )
}

split_seed <- 20261201L
fold_seed <- 20261202L
stability_seed <- 20261203L
development_fraction <- 0.75
fold_count <- 5L
stability_repetitions <- 12L
stability_fraction <- 0.80
penalty_points <- 60L
penalty_minimum_ratio <- 1e-4
support_tolerance <- 1e-8
numeric_tie_tolerance <- 1e-12

predictor_names <- c(
  "log_syct", "log_mmin", "log_mmax",
  "log1p_cach", "log1p_chmin", "log1p_chmax"
)
candidate_order <- c("ols", "ridge", "elastic_net", "lasso")
candidate_labels <- c(
  baseline = "development mean",
  ols = "OLS",
  ridge = "ridge",
  elastic_net = "elastic net",
  lasso = "lasso"
)
candidate_alpha <- c(ridge = 0, elastic_net = 0.5, lasso = 1)

write_tsv <- function(x, path) {
  write.table(
    x,
    file = path,
    sep = "\t",
    row.names = FALSE,
    quote = FALSE,
    na = "NA"
  )
}

root_mean_square_deviation <- function(x, center) {
  sqrt(colMeans(sweep(x, 2L, center, FUN = "-")^2))
}

fit_scaler <- function(x) {
  center <- colMeans(x)
  scale <- root_mean_square_deviation(x, center)
  if (any(!is.finite(scale)) || any(scale <= 0)) {
    stop("Every fitting predictor must have a positive finite scale.")
  }
  list(center = center, scale = scale)
}

apply_scaler <- function(x, scaler) {
  sweep(
    sweep(x, 2L, scaler$center, FUN = "-"),
    2L,
    scaler$scale,
    FUN = "/"
  )
}

fit_ols <- function(x, y) {
  fit <- lm.fit(cbind("(Intercept)" = 1, x), y)
  if (fit$rank != ncol(x) + 1L || any(!is.finite(fit$coefficients))) {
    stop("OLS design is not full rank or has non-finite coefficients.")
  }
  fit
}

predict_ols <- function(fit, x) {
  as.numeric(cbind("(Intercept)" = 1, x) %*% fit$coefficients)
}

make_folds <- function(n, count) {
  sample(rep(seq_len(count), length.out = n), size = n, replace = FALSE)
}

penalty_grid <- function(z, y, alpha) {
  centered_y <- y - mean(y)
  lambda_reference <- max(abs(drop(crossprod(z, centered_y)))) / nrow(z)
  if (!is.finite(lambda_reference) || lambda_reference <= 0) {
    stop("The development penalty reference must be positive and finite.")
  }
  if (alpha == 0) {
    ratio <- 10^seq(2, log10(penalty_minimum_ratio), length.out = penalty_points)
    lambda <- lambda_reference * ratio
    ratio_definition <- "lambda / lasso_reference; range 100 to 1e-4"
  } else {
    ratio <- 10^seq(0, log10(penalty_minimum_ratio), length.out = penalty_points)
    lambda_maximum <- lambda_reference / alpha
    lambda <- lambda_maximum * ratio
    ratio_definition <- "lambda / method_all_zero_lambda; range 1 to 1e-4"
  }
  list(
    lambda = lambda,
    ratio = ratio,
    reference = lambda_reference,
    ratio_definition = ratio_definition
  )
}

fit_penalty_path <- function(z, y, alpha, lambda) {
  glmnet::glmnet(
    x = z,
    y = y,
    family = "gaussian",
    alpha = alpha,
    lambda = lambda,
    intercept = TRUE,
    standardize = FALSE,
    control = list(thresh = 1e-10, maxit = 100000L)
  )
}

choose_grid_index <- function(mse) {
  eligible <- which(mse <= min(mse) + numeric_tie_tolerance)
  eligible[[1L]]
}

cross_validate_baseline_and_ols <- function(x, y, folds) {
  baseline_prediction <- rep(NA_real_, length(y))
  ols_prediction <- rep(NA_real_, length(y))
  for (fold in sort(unique(folds))) {
    analysis_rows <- folds != fold
    validation_rows <- !analysis_rows
    scaler <- fit_scaler(x[analysis_rows, , drop = FALSE])
    z_analysis <- apply_scaler(x[analysis_rows, , drop = FALSE], scaler)
    z_validation <- apply_scaler(x[validation_rows, , drop = FALSE], scaler)
    baseline_prediction[validation_rows] <- mean(y[analysis_rows])
    fit <- fit_ols(z_analysis, y[analysis_rows])
    ols_prediction[validation_rows] <- predict_ols(fit, z_validation)
  }
  stopifnot(!anyNA(baseline_prediction), !anyNA(ols_prediction))
  list(
    baseline_prediction = baseline_prediction,
    ols_prediction = ols_prediction,
    baseline_mse = mean((y - baseline_prediction)^2),
    ols_mse = mean((y - ols_prediction)^2)
  )
}

cross_validate_penalized <- function(x, y, folds, alpha) {
  squared_error_sum <- rep(0, penalty_points)
  validation_count <- 0L
  fold_records <- vector("list", length(sort(unique(folds))))
  for (fold in sort(unique(folds))) {
    analysis_rows <- folds != fold
    validation_rows <- !analysis_rows
    scaler <- fit_scaler(x[analysis_rows, , drop = FALSE])
    z_analysis <- apply_scaler(x[analysis_rows, , drop = FALSE], scaler)
    z_validation <- apply_scaler(x[validation_rows, , drop = FALSE], scaler)
    grid <- penalty_grid(z_analysis, y[analysis_rows], alpha)
    fit <- fit_penalty_path(z_analysis, y[analysis_rows], alpha, grid$lambda)
    predictions <- predict(
      fit,
      newx = z_validation,
      s = grid$lambda,
      type = "response"
    )
    predictions <- as.matrix(predictions)
    if (ncol(predictions) != penalty_points) {
      stop("The fitted penalty path did not return all requested values.")
    }
    errors <- sweep(predictions, 1L, y[validation_rows], FUN = "-")
    squared_error_sum <- squared_error_sum + colSums(errors^2)
    validation_count <- validation_count + sum(validation_rows)
    fold_records[[fold]] <- data.frame(
      fold = fold,
      grid_index = seq_len(penalty_points),
      relative_penalty = grid$ratio,
      lambda = grid$lambda,
      lambda_reference = grid$reference,
      stringsAsFactors = FALSE
    )
  }
  mse <- squared_error_sum / validation_count
  selected_index <- choose_grid_index(mse)
  list(
    mse = mse,
    rmse = sqrt(mse),
    selected_index = selected_index,
    fold_grids = do.call(rbind, fold_records)
  )
}

fit_final_penalized <- function(x, y, new_x, alpha, selected_index) {
  scaler <- fit_scaler(x)
  z <- apply_scaler(x, scaler)
  new_z <- apply_scaler(new_x, scaler)
  grid <- penalty_grid(z, y, alpha)
  fit <- fit_penalty_path(z, y, alpha, grid$lambda)
  selected_lambda <- grid$lambda[[selected_index]]
  prediction <- as.numeric(
    predict(fit, newx = new_z, s = selected_lambda, type = "response")
  )
  coefficient_z <- as.matrix(coef(fit, s = selected_lambda))[, 1L]
  slope_z <- coefficient_z[-1L]
  slope_original <- slope_z / scaler$scale
  intercept_original <- coefficient_z[[1L]] - sum(
    scaler$center * slope_original
  )
  coefficients <- c("(Intercept)" = intercept_original, slope_original)
  list(
    prediction = prediction,
    coefficients = coefficients,
    selected_lambda = selected_lambda,
    selected_relative_penalty = grid$ratio[[selected_index]],
    lambda_reference = grid$reference,
    scaler = scaler,
    fit = fit
  )
}

assessment_metrics <- function(y, prediction, development_mean) {
  errors <- y - prediction
  denominator <- sum((y - development_mean)^2)
  c(
    rmse = sqrt(mean(errors^2)),
    mae = mean(abs(errors)),
    r2_vs_development_mean = 1 - sum(errors^2) / denominator
  )
}

manual_vif <- function(x) {
  values <- vapply(
    seq_len(ncol(x)),
    function(column) {
      others <- x[, -column, drop = FALSE]
      fit <- lm.fit(cbind(1, others), x[, column])
      residual_sum <- sum(fit$residuals^2)
      total_sum <- sum((x[, column] - mean(x[, column]))^2)
      r_squared <- 1 - residual_sum / total_sum
      1 / (1 - r_squared)
    },
    numeric(1)
  )
  data.frame(term = colnames(x), vif = values, row.names = NULL)
}

markdown_table <- function(x, digits = 4) {
  paste(
    capture.output(
      knitr::kable(x, format = "pipe", digits = digits, row.names = FALSE)
    ),
    collapse = "\n"
  )
}

# Data provenance and analysis-ready copy ------------------------------------
raw_cpus <- MASS::cpus
raw_signature_before <- digest::digest(raw_cpus, algo = "sha256", serialize = TRUE)
stopifnot(
  nrow(raw_cpus) == 209L,
  ncol(raw_cpus) == 9L,
  sum(is.na(raw_cpus)) == 0L,
  all(raw_cpus$perf > 0),
  all(raw_cpus$syct > 0),
  all(raw_cpus$mmin > 0),
  all(raw_cpus$mmax > 0),
  all(raw_cpus$cach >= 0),
  all(raw_cpus$chmin >= 0),
  all(raw_cpus$chmax >= 0)
)

analysis_data <- data.frame(
  row_id = seq_len(nrow(raw_cpus)),
  name = as.character(raw_cpus$name),
  perf = raw_cpus$perf,
  syct = raw_cpus$syct,
  mmin = raw_cpus$mmin,
  mmax = raw_cpus$mmax,
  cach = raw_cpus$cach,
  chmin = raw_cpus$chmin,
  chmax = raw_cpus$chmax,
  log_perf = log(raw_cpus$perf),
  log_syct = log(raw_cpus$syct),
  log_mmin = log(raw_cpus$mmin),
  log_mmax = log(raw_cpus$mmax),
  log1p_cach = log1p(raw_cpus$cach),
  log1p_chmin = log1p(raw_cpus$chmin),
  log1p_chmax = log1p(raw_cpus$chmax),
  stringsAsFactors = FALSE
)

data_dictionary <- data.frame(
  source_variable = c(
    "name", "perf", "estperf", "syct", "mmin", "mmax",
    "cach", "chmin", "chmax"
  ),
  unit_or_definition = c(
    "manufacturer and model identifier",
    "published benchmark performance relative to IBM 370/158-3",
    "performance estimated by the original authors' regression",
    "nanoseconds", "kilobytes", "kilobytes", "kilobytes",
    "channel count", "channel count"
  ),
  study_role = c(
    "identifier only", "response source", "excluded derived prediction",
    rep("eligible predictor", 6L)
  ),
  analysis_representation = c(
    "character ID", "log_perf = log(perf)", "not used",
    "log_syct = log(syct)", "log_mmin = log(mmin)",
    "log_mmax = log(mmax)", "log1p_cach = log1p(cach)",
    "log1p_chmin = log1p(chmin)", "log1p_chmax = log1p(chmax)"
  ),
  stringsAsFactors = FALSE
)

raw_signature_after <- digest::digest(MASS::cpus, algo = "sha256", serialize = TRUE)
stopifnot(
  identical(raw_cpus, MASS::cpus),
  identical(raw_signature_before, raw_signature_after),
  !anyNA(analysis_data),
  all(vapply(analysis_data[predictor_names], is.numeric, logical(1)))
)

# Frozen data roles and development-only tuning ------------------------------
set.seed(split_seed)
development_rows <- sort(sample(
  seq_len(nrow(analysis_data)),
  size = floor(development_fraction * nrow(analysis_data)),
  replace = FALSE
))
assessment_rows <- setdiff(seq_len(nrow(analysis_data)), development_rows)
stopifnot(length(development_rows) == 156L, length(assessment_rows) == 53L)

role <- rep("assessment", nrow(analysis_data))
role[development_rows] <- "development"
split_ledger <- analysis_data[, c("row_id", "name", "perf", "log_perf")]
split_ledger$role <- role

x_all <- as.matrix(analysis_data[, predictor_names])
y_all <- analysis_data$log_perf
x_development <- x_all[development_rows, , drop = FALSE]
y_development <- y_all[development_rows]
x_assessment <- x_all[assessment_rows, , drop = FALSE]
y_assessment <- y_all[assessment_rows]

set.seed(fold_seed)
development_folds <- make_folds(length(development_rows), fold_count)
fold_ledger <- data.frame(
  row_id = development_rows,
  fold = development_folds,
  stringsAsFactors = FALSE
)
stopifnot(all(table(development_folds) %in% c(31L, 32L)))

cv_simple <- cross_validate_baseline_and_ols(
  x_development,
  y_development,
  development_folds
)
cv_penalized <- lapply(
  candidate_alpha,
  function(alpha) {
    cross_validate_penalized(
      x_development,
      y_development,
      development_folds,
      alpha
    )
  }
)

cv_results <- rbind(
  data.frame(
    model = "baseline",
    grid_index = NA_integer_,
    relative_penalty = NA_real_,
    cv_mse = cv_simple$baseline_mse,
    cv_rmse = sqrt(cv_simple$baseline_mse),
    stringsAsFactors = FALSE
  ),
  data.frame(
    model = "ols",
    grid_index = NA_integer_,
    relative_penalty = NA_real_,
    cv_mse = cv_simple$ols_mse,
    cv_rmse = sqrt(cv_simple$ols_mse),
    stringsAsFactors = FALSE
  ),
  do.call(
    rbind,
    lapply(names(cv_penalized), function(model) {
      item <- cv_penalized[[model]]
      data.frame(
        model = model,
        grid_index = seq_len(penalty_points),
        relative_penalty = item$fold_grids$relative_penalty[
          item$fold_grids$fold == min(item$fold_grids$fold)
        ],
        cv_mse = item$mse,
        cv_rmse = item$rmse,
        stringsAsFactors = FALSE
      )
    })
  )
)

cv_summary <- data.frame(
  model = c("baseline", candidate_order),
  selected_grid_index = c(
    NA_integer_,
    NA_integer_,
    vapply(
      cv_penalized[c("ridge", "elastic_net", "lasso")],
      function(x) x$selected_index,
      integer(1)
    )
  ),
  selected_relative_penalty = c(
    NA_real_,
    NA_real_,
    vapply(
      cv_penalized[c("ridge", "elastic_net", "lasso")],
      function(x) {
        fold_one <- x$fold_grids[x$fold_grids$fold == 1L, ]
        fold_one$relative_penalty[[x$selected_index]]
      },
      numeric(1)
    )
  ),
  cv_rmse = c(
    sqrt(cv_simple$baseline_mse),
    sqrt(cv_simple$ols_mse),
    vapply(
      cv_penalized[c("ridge", "elastic_net", "lasso")],
      function(x) x$rmse[[x$selected_index]],
      numeric(1)
    )
  ),
  stringsAsFactors = FALSE
)
cv_summary$label <- unname(candidate_labels[cv_summary$model])
cv_summary <- cv_summary[, c(
  "model", "label", "selected_grid_index",
  "selected_relative_penalty", "cv_rmse"
)]

eligible_summary <- cv_summary[cv_summary$model %in% candidate_order, ]
minimum_cv <- min(eligible_summary$cv_rmse)
eligible_models <- eligible_summary$model[
  eligible_summary$cv_rmse <= minimum_cv + numeric_tie_tolerance
]
selected_model <- candidate_order[candidate_order %in% eligible_models][[1L]]
selected_summary <- cv_summary[cv_summary$model == selected_model, ]

# Fit the predeclared fixed OLS inference track on development rows only.
inference_frame <- analysis_data[development_rows, c("log_perf", predictor_names)]
inference_formula <- as.formula(
  paste("log_perf ~", paste(predictor_names, collapse = " + "))
)
inference_fit <- lm(inference_formula, data = inference_frame)
inference_summary <- summary(inference_fit)
coefficient_matrix <- inference_summary$coefficients
critical_value <- qt(0.975, df = df.residual(inference_fit))
ols_coefficients <- data.frame(
  term = rownames(coefficient_matrix),
  estimate = coefficient_matrix[, "Estimate"],
  standard_error = coefficient_matrix[, "Std. Error"],
  t_value = coefficient_matrix[, "t value"],
  p_value = coefficient_matrix[, "Pr(>|t|)"],
  lower_95 = coefficient_matrix[, "Estimate"] -
    critical_value * coefficient_matrix[, "Std. Error"],
  upper_95 = coefficient_matrix[, "Estimate"] +
    critical_value * coefficient_matrix[, "Std. Error"],
  row.names = NULL,
  stringsAsFactors = FALSE
)
vif_table <- manual_vif(as.matrix(inference_frame[, predictor_names]))

influence <- influence.measures(inference_fit)
leverage <- hatvalues(inference_fit)
cook <- cooks.distance(inference_fit)
standardized_residual <- rstandard(inference_fit)
diagnostic_summary <- data.frame(
  quantity = c(
    "development rows", "residual degrees of freedom", "residual sigma",
    "R-squared", "adjusted R-squared", "maximum absolute standardized residual",
    "maximum leverage", "maximum Cook distance", "rows removed after diagnostics"
  ),
  value = c(
    nrow(inference_frame),
    df.residual(inference_fit),
    inference_summary$sigma,
    inference_summary$r.squared,
    inference_summary$adj.r.squared,
    max(abs(standardized_residual)),
    max(leverage),
    max(cook),
    0
  ),
  stringsAsFactors = FALSE
)

# Refit the development-selected predictive procedure before assessment use.
development_mean <- mean(y_development)
if (selected_model == "ols") {
  final_scaler <- fit_scaler(x_development)
  final_ols <- fit_ols(apply_scaler(x_development, final_scaler), y_development)
  selected_prediction <- predict_ols(
    final_ols,
    apply_scaler(x_assessment, final_scaler)
  )
  slope_z <- final_ols$coefficients[-1L]
  slope_original <- slope_z / final_scaler$scale
  intercept_original <- final_ols$coefficients[[1L]] - sum(
    final_scaler$center * slope_original
  )
  final_coefficients_vector <- c(
    "(Intercept)" = intercept_original,
    slope_original
  )
  selected_lambda <- NA_real_
  selected_relative_penalty <- NA_real_
  lambda_reference <- NA_real_
} else {
  selected_index <- selected_summary$selected_grid_index[[1L]]
  final_penalized <- fit_final_penalized(
    x_development,
    y_development,
    x_assessment,
    candidate_alpha[[selected_model]],
    selected_index
  )
  selected_prediction <- final_penalized$prediction
  final_coefficients_vector <- final_penalized$coefficients
  selected_lambda <- final_penalized$selected_lambda
  selected_relative_penalty <- final_penalized$selected_relative_penalty
  lambda_reference <- final_penalized$lambda_reference
}

baseline_prediction <- rep(development_mean, length(assessment_rows))
selected_metrics <- assessment_metrics(
  y_assessment,
  selected_prediction,
  development_mean
)
baseline_metrics <- assessment_metrics(
  y_assessment,
  baseline_prediction,
  development_mean
)
assessment_summary <- rbind(
  data.frame(
    model = "baseline",
    label = candidate_labels[["baseline"]],
    rmse = baseline_metrics[["rmse"]],
    mae = baseline_metrics[["mae"]],
    r2_vs_development_mean = baseline_metrics[["r2_vs_development_mean"]]
  ),
  data.frame(
    model = selected_model,
    label = candidate_labels[[selected_model]],
    rmse = selected_metrics[["rmse"]],
    mae = selected_metrics[["mae"]],
    r2_vs_development_mean = selected_metrics[["r2_vs_development_mean"]]
  )
)

assessment_predictions <- data.frame(
  row_id = assessment_rows,
  name = analysis_data$name[assessment_rows],
  observed_perf = analysis_data$perf[assessment_rows],
  observed_log_perf = y_assessment,
  predicted_log_perf = selected_prediction,
  baseline_log_perf = baseline_prediction,
  median_scale_prediction = exp(selected_prediction),
  log_error = y_assessment - selected_prediction,
  stringsAsFactors = FALSE
)
final_coefficients <- data.frame(
  term = names(final_coefficients_vector),
  coefficient_on_transformed_predictor_scale = as.numeric(
    final_coefficients_vector
  ),
  selected = abs(as.numeric(final_coefficients_vector)) > support_tolerance,
  stringsAsFactors = FALSE
)
final_coefficients$selected[final_coefficients$term == "(Intercept)"] <- TRUE

# Development-only stability ledger. Each subsample repeats five-fold tuning.
set.seed(stability_seed)
stability_rows <- vector("list", stability_repetitions * 2L)
record_index <- 1L
for (repetition in seq_len(stability_repetitions)) {
  local_rows <- sort(sample(
    seq_len(nrow(x_development)),
    size = floor(stability_fraction * nrow(x_development)),
    replace = FALSE
  ))
  local_x <- x_development[local_rows, , drop = FALSE]
  local_y <- y_development[local_rows]
  local_folds <- make_folds(length(local_rows), fold_count)
  for (method in c("elastic_net", "lasso")) {
    local_cv <- cross_validate_penalized(
      local_x,
      local_y,
      local_folds,
      candidate_alpha[[method]]
    )
    local_fit <- fit_final_penalized(
      local_x,
      local_y,
      local_x[1L, , drop = FALSE],
      candidate_alpha[[method]],
      local_cv$selected_index
    )
    selected_slopes <- abs(local_fit$coefficients[-1L]) > support_tolerance
    stability_rows[[record_index]] <- data.frame(
      repetition = repetition,
      model = method,
      selected_grid_index = local_cv$selected_index,
      selected_relative_penalty = local_fit$selected_relative_penalty,
      t(as.integer(selected_slopes)),
      check.names = FALSE,
      stringsAsFactors = FALSE
    )
    names(stability_rows[[record_index]])[-(1:4)] <- predictor_names
    record_index <- record_index + 1L
  }
}
stability_ledger <- do.call(rbind, stability_rows)
selection_stability <- do.call(
  rbind,
  lapply(c("elastic_net", "lasso"), function(method) {
    rows <- stability_ledger$model == method
    frequencies <- colMeans(stability_ledger[rows, predictor_names, drop = FALSE])
    data.frame(
      model = method,
      term = predictor_names,
      selected_count = as.integer(frequencies * stability_repetitions),
      repetitions = stability_repetitions,
      selection_frequency = as.numeric(frequencies),
      stringsAsFactors = FALSE
    )
  })
)

# Files and figures ----------------------------------------------------------
write.csv(analysis_data, file.path(output_directory, "analysis_ready.csv"), row.names = FALSE)
write_tsv(data_dictionary, file.path(output_directory, "data_dictionary.tsv"))
write.csv(split_ledger, file.path(output_directory, "split_ledger.csv"), row.names = FALSE)
write_tsv(fold_ledger, file.path(output_directory, "development_folds.tsv"))
write_tsv(cv_results, file.path(output_directory, "cv_results.tsv"))
write_tsv(cv_summary, file.path(output_directory, "cv_summary.tsv"))
write_tsv(ols_coefficients, file.path(output_directory, "ols_coefficients.tsv"))
write_tsv(vif_table, file.path(output_directory, "vif.tsv"))
write_tsv(diagnostic_summary, file.path(output_directory, "diagnostic_summary.tsv"))
write.csv(
  assessment_predictions,
  file.path(output_directory, "assessment_predictions.csv"),
  row.names = FALSE
)
write_tsv(assessment_summary, file.path(output_directory, "assessment_metrics.tsv"))
write_tsv(final_coefficients, file.path(output_directory, "final_coefficients.tsv"))
write_tsv(stability_ledger, file.path(output_directory, "stability_ledger.tsv"))
write_tsv(selection_stability, file.path(output_directory, "selection_stability.tsv"))

ink <- "#183848"
accent <- "#A14C32"
light_ink <- "#6D8792"
light_accent <- "#D69A83"
neutral <- "#D7DEE1"

png(
  file.path(output_directory, "ch12_diagnostics.png"),
  width = 1900,
  height = 1500,
  res = 180,
  bg = "white"
)
par(mfrow = c(2, 2), mar = c(4.3, 4.4, 2.7, 1.0), las = 1)
plot(
  inference_fit$fitted.values,
  residuals(inference_fit),
  pch = 19,
  col = adjustcolor(ink, alpha.f = 0.70),
  xlab = "Fitted log performance",
  ylab = "Residual",
  main = "Residual level and spread"
)
abline(h = 0, col = accent, lwd = 2)
lines(lowess(inference_fit$fitted.values, residuals(inference_fit)), col = light_accent, lwd = 2)

qqnorm(
  standardized_residual,
  pch = 19,
  col = adjustcolor(ink, alpha.f = 0.70),
  main = "Standardized residual Q-Q",
  xlab = "Normal reference quantile",
  ylab = "Standardized residual"
)
qqline(standardized_residual, col = accent, lwd = 2)

plot(
  leverage,
  cook,
  pch = 19,
  col = adjustcolor(accent, alpha.f = 0.72),
  xlab = "Leverage",
  ylab = "Cook distance",
  main = "Geometry and influence"
)
largest_cook <- order(cook, decreasing = TRUE)[1:3]
text(
  leverage[largest_cook],
  cook[largest_cook],
  labels = development_rows[largest_cook],
  pos = 3,
  cex = 0.72,
  col = ink
)

correlation <- cor(x_development)
image(
  seq_len(ncol(correlation)),
  seq_len(ncol(correlation)),
  t(correlation[nrow(correlation):1, ]),
  col = colorRampPalette(c(light_accent, "white", light_ink))(100),
  zlim = c(-1, 1),
  axes = FALSE,
  xlab = "",
  ylab = "",
  main = "Transformed-predictor correlation"
)
axis(1, at = seq_along(predictor_names), labels = predictor_names, las = 2, cex.axis = 0.68)
axis(
  2,
  at = seq_along(predictor_names),
  labels = rev(predictor_names),
  las = 2,
  cex.axis = 0.68
)
box()
dev.off()

png(
  file.path(output_directory, "ch12_model_evidence.png"),
  width = 2400,
  height = 1000,
  res = 180,
  bg = "white"
)
par(mfrow = c(1, 3), mar = c(4.8, 4.5, 2.8, 1.0), las = 1)

penalty_colors <- c(ridge = light_ink, elastic_net = accent, lasso = ink)
plot(
  NA,
  xlim = c(0, 4),
  ylim = range(cv_results$cv_rmse[is.finite(cv_results$relative_penalty)]),
  xlab = "Penalty path position, -log10(relative penalty)",
  ylab = "Development CV-RMSE",
  main = "Selection stays in development"
)
for (method in names(penalty_colors)) {
  rows <- cv_results$model == method
  lines(
    -log10(cv_results$relative_penalty[rows]),
    cv_results$cv_rmse[rows],
    col = penalty_colors[[method]],
    lwd = 3
  )
  chosen <- cv_summary[cv_summary$model == method, ]
  points(
    -log10(chosen$selected_relative_penalty),
    chosen$cv_rmse,
    pch = 19,
    col = penalty_colors[[method]],
    cex = 1.1
  )
}
abline(h = cv_summary$cv_rmse[cv_summary$model == "ols"], col = "#666666", lty = 2, lwd = 2)
legend(
  "topright",
  legend = c("ridge", "elastic net", "lasso", "OLS"),
  col = c(penalty_colors, "#666666"),
  lty = c(1, 1, 1, 2),
  lwd = 2,
  bty = "n",
  cex = 0.78
)

plot(
  y_assessment,
  selected_prediction,
  pch = 19,
  col = adjustcolor(ink, alpha.f = 0.75),
  xlab = "Observed log performance",
  ylab = "Predicted log performance",
  main = paste("Locked assessment:", candidate_labels[[selected_model]])
)
abline(0, 1, col = accent, lwd = 2)
abline(h = development_mean, col = light_ink, lty = 2, lwd = 2)
legend(
  "topleft",
  legend = c("selected procedure", "development mean"),
  col = c(accent, light_ink),
  lty = c(1, 2),
  lwd = 2,
  bty = "n",
  cex = 0.78
)

stability_matrix <- reshape(
  selection_stability[, c("model", "term", "selection_frequency")],
  idvar = "term",
  timevar = "model",
  direction = "wide"
)
stability_matrix <- stability_matrix[
  match(predictor_names, stability_matrix$term),
]
barplot(
  t(as.matrix(stability_matrix[, -1, drop = FALSE])),
  beside = TRUE,
  names.arg = sub("^log1?p?_?", "", predictor_names),
  las = 2,
  ylim = c(0, 1),
  col = c(accent, ink),
  border = NA,
  ylab = "Selection frequency",
  main = "Twelve development subsamples"
)
legend(
  "topright",
  legend = c("elastic net", "lasso"),
  fill = c(accent, ink),
  border = NA,
  bty = "n",
  cex = 0.78
)
dev.off()

report_lines <- c(
  "# Chapter 12 frozen study report",
  "",
  paste("Generated from `MASS::cpus` with split seed", split_seed, "and fold seed", fold_seed, "."),
  "All model selection used development rows. The assessment outcomes were used once after the procedure was selected.",
  "",
  "## Data roles",
  "",
  markdown_table(data_dictionary, digits = 4),
  "",
  "## Development cross-validation",
  "",
  markdown_table(cv_summary, digits = 6),
  "",
  paste("Selected procedure:", candidate_labels[[selected_model]], "."),
  "",
  "## Locked assessment",
  "",
  markdown_table(assessment_summary, digits = 6),
  "",
  "## Fixed OLS diagnostic summary",
  "",
  markdown_table(diagnostic_summary, digits = 6),
  "",
  "## Development-only selection frequencies",
  "",
  markdown_table(selection_stability, digits = 3),
  "",
  "## Claim boundary",
  "",
  paste(
    "The data are historical, the sampling mechanism does not establish a current target population,",
    "and one 53-row assessment split does not establish stable or external prediction accuracy."
  )
)
writeLines(report_lines, file.path(output_directory, "study_report.md"))

run_record <- c(
  paste("source object", "MASS::cpus"),
  paste("raw serialized sha256", raw_signature_before),
  paste("raw object unchanged", identical(raw_cpus, MASS::cpus)),
  paste("R rows", nrow(analysis_data)),
  paste("missing cells", sum(is.na(raw_cpus))),
  paste("response", "log_perf = log(perf)"),
  paste("predictors", paste(predictor_names, collapse = ",")),
  paste("excluded identifier", "name"),
  paste("excluded derived prediction", "estperf"),
  paste("split seed", split_seed),
  paste("development rows", length(development_rows)),
  paste("assessment rows", length(assessment_rows)),
  paste("development indices", paste(development_rows, collapse = ",")),
  paste("assessment indices", paste(assessment_rows, collapse = ",")),
  paste("fold seed", fold_seed),
  paste("fold assignment", paste(development_folds, collapse = ",")),
  paste("candidate order", paste(candidate_order, collapse = ",")),
  paste("penalty points", penalty_points),
  paste("penalty minimum ratio", penalty_minimum_ratio),
  paste("selected model", selected_model),
  paste("selected label", candidate_labels[[selected_model]]),
  paste("selected lambda", format(selected_lambda, digits = 16)),
  paste("selected relative penalty", format(selected_relative_penalty, digits = 16)),
  paste("lambda reference", format(lambda_reference, digits = 16)),
  paste("assessment opened after selection", TRUE),
  paste("assessment selected RMSE", format(selected_metrics[["rmse"]], digits = 16)),
  paste("assessment selected MAE", format(selected_metrics[["mae"]], digits = 16)),
  paste(
    "assessment selected R2 vs development mean",
    format(selected_metrics[["r2_vs_development_mean"]], digits = 16)
  ),
  paste("stability seed", stability_seed),
  paste("stability repetitions", stability_repetitions),
  paste("stability subsample size", floor(stability_fraction * nrow(x_development))),
  paste("rows removed after diagnostics", 0),
  paste("formula", deparse(inference_formula)),
  paste("raw data modified", FALSE)
)
writeLines(run_record, file.path(output_directory, "run_record.txt"))
writeLines(capture.output(sessionInfo()), file.path(output_directory, "session_info.txt"))
writeLines(
  c(
    "[PASS] Frozen Chapter 12 study completed.",
    "All selection used development rows.",
    "Assessment outcomes were used once after selection.",
    "Raw MASS::cpus data remained unchanged.",
    "No observation was removed after diagnostics.",
    "The result is an internal historical teaching illustration, not external validation."
  ),
  file.path(output_directory, "verification.txt")
)

files_before_manifest <- sort(list.files(output_directory, full.names = TRUE))
manifest <- data.frame(
  file = basename(files_before_manifest),
  bytes = as.numeric(file.info(files_before_manifest)$size),
  sha256 = vapply(
    files_before_manifest,
    function(path) digest::digest(file = path, algo = "sha256"),
    character(1)
  ),
  stringsAsFactors = FALSE
)
write_tsv(manifest, file.path(output_directory, "manifest_sha256.tsv"))

expected_files <- sort(c(
  "analysis_ready.csv",
  "assessment_metrics.tsv",
  "assessment_predictions.csv",
  "ch12_diagnostics.png",
  "ch12_model_evidence.png",
  "cv_results.tsv",
  "cv_summary.tsv",
  "data_dictionary.tsv",
  "development_folds.tsv",
  "diagnostic_summary.tsv",
  "final_coefficients.tsv",
  "manifest_sha256.tsv",
  "ols_coefficients.tsv",
  "run_record.txt",
  "selection_stability.tsv",
  "session_info.txt",
  "split_ledger.csv",
  "stability_ledger.tsv",
  "study_report.md",
  "verification.txt",
  "vif.tsv"
))
created_files <- sort(list.files(output_directory))
stopifnot(identical(created_files, expected_files))

cat("[PASS] Frozen Chapter 12 study completed.\n")
cat("Selected procedure:", candidate_labels[[selected_model]], "\n")
cat("Development CV summary:\n")
print(cv_summary, row.names = FALSE, digits = 6)
cat("Locked assessment summary:\n")
print(assessment_summary, row.names = FALSE, digits = 6)
cat("Output directory:\n", normalizePath(output_directory), "\n", sep = "")
