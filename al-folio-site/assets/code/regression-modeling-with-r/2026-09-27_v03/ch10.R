# Chapter 10. Lasso, Elastic Net, and Selection Stability
# Reasoning Through Regression: Inference, Prediction, and Regularization with R
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 243 =====
soft_threshold <- function(a, gamma) {
  sign(a) * pmax(abs(a) - gamma, 0)
}

z_orth <- cbind(
  z1 = c(-1, -1, 1, 1),
  z2 = c(-1, 1, -1, 1)
)
y_orth <- as.vector(3 * z_orth[, 1] - 1.5 * z_orth[, 2])
score <- colMeans(z_orth * y_orth)

lasso_closed <- soft_threshold(score, gamma = 1)
enet_closed <- soft_threshold(score, gamma = 0.5) / 1.5
ridge_closed <- score / 2
rbind(score, lasso_closed, enet_closed, ridge_closed)

# ===== Book block 2; source line 294 =====
enet_cd <- function(z, yc, lambda, alpha, start = NULL,
                    tol = 1e-8, max_iter = 20000L) {
  p <- ncol(z)
  beta <- if (is.null(start)) numeric(p) else start
  for (iteration in seq_len(max_iter)) {
    old <- beta
    for (j in seq_len(p)) {
      partial <- yc - as.vector(z %*% beta) + z[, j] * beta[j]
      score_j <- mean(z[, j] * partial)
      curvature <- mean(z[, j]^2) + lambda * (1 - alpha)
      beta[j] <- soft_threshold(score_j, lambda * alpha) / curvature
    }
    if (max(abs(beta - old)) < tol) break
  }
  residual <- yc - as.vector(z %*% beta)
  score <- colMeans(z * residual)
  active <- abs(beta) > tol
  violation <- numeric(p)
  violation[active] <- abs(
    score[active] - lambda * (1 - alpha) * beta[active] -
      lambda * alpha * sign(beta[active])
  )
  violation[!active] <- pmax(
    abs(score[!active]) - lambda * alpha, 0
  )
  list(beta = beta, iterations = iteration,
       kkt = max(violation), converged = iteration < max_iter)
}

fit_check <- enet_cd(z_orth, y_orth, lambda = 1, alpha = 1)
stopifnot(max(abs(fit_check$beta - lasso_closed)) < 1e-7)
stopifnot(fit_check$kkt < 1e-7)
fit_check

# ===== Book block 3; source line 382 =====
prepare_xy <- function(x, y) {
  x <- as.matrix(x)
  center <- colMeans(x)
  z <- sweep(x, 2, center, "-")
  scale <- sqrt(colMeans(z^2))
  if (any(scale <= 0)) stop("A fitting predictor is constant.")
  list(z = sweep(z, 2, scale, "/"), yc = y - mean(y),
       center = center, scale = scale, ybar = mean(y))
}

fit_path <- function(x, y, lambda, alpha) {
  prep <- prepare_xy(x, y)
  lambda <- sort(lambda, decreasing = TRUE)
  b_std <- matrix(0, ncol(x), length(lambda))
  b_raw <- b_std
  intercept <- numeric(length(lambda))
  kkt <- numeric(length(lambda))
  start <- numeric(ncol(x))
  for (m in seq_along(lambda)) {
    fit <- enet_cd(prep$z, prep$yc, lambda[m], alpha, start)
    if (!fit$converged || fit$kkt > 1e-6) stop("Fit check failed.")
    start <- fit$beta
    b_std[, m] <- fit$beta
    b_raw[, m] <- fit$beta / prep$scale
    intercept[m] <- prep$ybar - sum(b_raw[, m] * prep$center)
    kkt[m] <- fit$kkt
  }
  rownames(b_raw) <- rownames(b_std) <- colnames(x)
  list(lambda = lambda, beta = b_raw, beta_std = b_std,
       intercept = intercept, kkt = kkt)
}

predict_path <- function(path, newx) {
  sweep(as.matrix(newx) %*% path$beta, 2, path$intercept, "+")
}

lambda_grid <- function(x, y, alpha) {
  prep <- prepare_xy(x, y)
  top <- max(abs(colMeans(prep$z * prep$yc))) / alpha
  if (!is.finite(top) || top <= 0) stop("Positive penalty threshold required.")
  top * exp(seq(0, log(0.02), length.out = 25))
}

cv_enet <- function(x, y, alpha, fold_id) {
  folds <- sort(unique(fold_id))
  stopifnot(length(fold_id) == nrow(x), length(folds) >= 2,
            !anyNA(fold_id), length(y) == nrow(x), alpha > 0)
  ratio <- exp(seq(0, log(0.02), length.out = 25))
  fold_sse <- fold_lambda <- matrix(NA_real_, length(folds), length(ratio))
  fold_n <- integer(length(folds))
  fold_kkt <- numeric(length(folds))
  for (k in seq_along(folds)) {
    hold <- fold_id == folds[k]
    lambda_k <- lambda_grid(x[!hold, , drop = FALSE], y[!hold], alpha)
    path <- fit_path(x[!hold, , drop = FALSE], y[!hold], lambda_k, alpha)
    pred <- predict_path(path, x[hold, , drop = FALSE])
    fold_sse[k, ] <- colSums((y[hold] - pred)^2)
    fold_lambda[k, ] <- lambda_k
    fold_n[k] <- sum(hold)
    fold_kkt[k] <- max(path$kkt)
  }
  cv_mse <- colSums(fold_sse) / sum(fold_n)
  chosen <- which.min(cv_mse)
  lambda <- lambda_grid(x, y, alpha)
  path <- fit_path(x, y, lambda, alpha)
  list(lambda = lambda, cv_mse = cv_mse, chosen = chosen,
       selected_lambda = lambda[chosen], path = path,
       beta = path$beta[, chosen], intercept = path$intercept[chosen],
       ratio = ratio, selected_ratio = ratio[chosen],
       fold_sse = fold_sse, fold_n = fold_n, fold_lambda = fold_lambda,
       max_kkt = max(fold_kkt, path$kkt))
}

balanced_folds <- function(n, k, seed) {
  set.seed(seed)
  sample(rep(seq_len(k), length.out = n))
}

set.seed(20260905)
n <- 180
g1 <- rnorm(n); g2 <- rnorm(n)
x <- cbind(
  x1 = g1 + rnorm(n, sd = 0.08),
  x2 = g1 + rnorm(n, sd = 0.08),
  x3 = g2 + rnorm(n, sd = 0.10),
  x4 = g2 + rnorm(n, sd = 0.10),
  x5 = rnorm(n), x6 = rnorm(n), x7 = rnorm(n), x8 = rnorm(n)
)
truth <- c(x1 = 2, x2 = 0, x3 = -1.5, x4 = 0,
           x5 = 1, x6 = 0, x7 = 0, x8 = 0)
y <- 1 + as.vector(x %*% truth) + rnorm(n, sd = 1)
development <- 1:120; assessment <- 121:180
fold_id <- balanced_folds(120, 5, seed = 20261001)

lasso <- cv_enet(x[development, ], y[development], 1, fold_id)
enet <- cv_enet(x[development, ], y[development], 0.5, fold_id)
predict_one <- function(fit, newx) {
  as.vector(fit$intercept + as.matrix(newx) %*% fit$beta)
}
result <- data.frame(
  method = c("lasso", "elastic net"),
  lambda = c(lasso$selected_lambda, enet$selected_lambda),
  cv_rmse = sqrt(c(min(lasso$cv_mse), min(enet$cv_mse))),
  assessment_rmse = c(
    sqrt(mean((y[assessment] -
      predict_one(lasso, x[assessment, ]))^2)),
    sqrt(mean((y[assessment] -
      predict_one(enet, x[assessment, ]))^2))
  ),
  selected = c(sum(abs(lasso$beta) > 1e-8),
               sum(abs(enet$beta) > 1e-8))
)
transform(result, lambda = round(lambda, 5),
          cv_rmse = round(cv_rmse, 4),
          assessment_rmse = round(assessment_rmse, 4))

# ===== Book block 4; source line 585 =====
selection_ledger <- function(x, y, alpha, seed) {
  repetitions <- 12
  sample_size <- floor(0.70 * nrow(x))
  selected <- matrix(FALSE, repetitions, ncol(x),
                     dimnames = list(NULL, colnames(x)))
  set.seed(seed)
  sample_seeds <- sample.int(.Machine$integer.max, repetitions)
  fold_seeds <- sample.int(.Machine$integer.max, repetitions)
  for (b in seq_len(repetitions)) {
    set.seed(sample_seeds[b])
    rows <- sort(sample.int(nrow(x), sample_size))
    folds <- balanced_folds(sample_size, 5, fold_seeds[b])
    fit <- cv_enet(x[rows, , drop = FALSE], y[rows], alpha, folds)
    selected[b, ] <- abs(fit$beta) > 1e-8
  }
  colMeans(selected)
}

freq_lasso <- selection_ledger(
  x[development, ], y[development], alpha = 1, seed = 20261012
)
freq_enet <- selection_ledger(
  x[development, ], y[development], alpha = 0.5, seed = 20261012
)
round(rbind(lasso = freq_lasso, elastic_net = freq_enet), 3)

# ===== Book block 5; source line 671 =====
data(mtcars, package = "datasets")
mt_x <- as.matrix(mtcars[, c("wt", "disp", "hp", "drat", "qsec")])
mt_y <- mtcars$mpg
set.seed(20261020)
mt_assessment <- sort(sample(seq_len(nrow(mt_x)), 8))
mt_development <- setdiff(seq_len(nrow(mt_x)), mt_assessment)
mt_fold <- balanced_folds(
  length(mt_development), 4, seed = 20261021
)

mt_lasso <- cv_enet(
  mt_x[mt_development, ], mt_y[mt_development], 1, mt_fold
)
mt_enet <- cv_enet(
  mt_x[mt_development, ], mt_y[mt_development], 0.5, mt_fold
)
mt_result <- data.frame(
  method = c("lasso", "elastic net"),
  selected = c(
    paste(names(mt_lasso$beta)[abs(mt_lasso$beta) > 1e-8],
          collapse = ", "),
    paste(names(mt_enet$beta)[abs(mt_enet$beta) > 1e-8],
          collapse = ", ")
  ),
  assessment_rmse = c(
    sqrt(mean((mt_y[mt_assessment] -
      predict_one(mt_lasso, mt_x[mt_assessment, ]))^2)),
    sqrt(mean((mt_y[mt_assessment] -
      predict_one(mt_enet, mt_x[mt_assessment, ]))^2))
  )
)
mt_assessment
transform(mt_result, assessment_rmse = round(assessment_rmse, 4))
