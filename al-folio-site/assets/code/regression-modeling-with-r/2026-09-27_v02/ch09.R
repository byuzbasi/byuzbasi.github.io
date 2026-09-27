# Chapter 9. Bias, Variance, and Ridge Regression
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 439 =====
ridge_fit <- function(x, y, lambda) {
  x <- as.matrix(x)
  y <- as.numeric(y)
  stopifnot(is.numeric(x), is.numeric(y), nrow(x) == length(y))
  stopifnot(all(is.finite(x)), all(is.finite(y)))
  stopifnot(length(lambda) == 1L, is.finite(lambda), lambda >= 0)

  x_center <- colMeans(x)
  x_scale <- apply(x, 2, sd)
  stopifnot(all(is.finite(x_scale)), all(x_scale > 0))
  y_center <- mean(y)
  z <- sweep(sweep(x, 2, x_center, "-"), 2, x_scale, "/")
  yc <- y - y_center

  decomposition <- svd(z, nu = ncol(z), nv = ncol(z))
  tolerance <- max(dim(z)) *
    max(decomposition$d) * .Machine$double.eps
  if (lambda == 0 && any(decomposition$d <= tolerance)) {
    stop(paste0(
      "lambda = 0 requires full column rank ",
      "in this teaching function"
    ))
  }
  multiplier <- if (lambda == 0) {
    1 / decomposition$d
  } else {
    decomposition$d / (decomposition$d^2 + lambda)
  }
  beta_z <- drop(
    decomposition$v %*%
      (multiplier * drop(crossprod(decomposition$u, yc)))
  )
  beta_x <- beta_z / x_scale
  intercept <- y_center - sum(beta_x * x_center)

  structure(
    list(
      lambda = lambda, intercept = intercept, beta = beta_x,
      beta_z = beta_z, x_center = x_center, x_scale = x_scale,
      singular_values = decomposition$d,
      fitted = drop(intercept + x %*% beta_x)
    ),
    class = "chapter9_ridge"
  )
}

predict.chapter9_ridge <- function(object, newdata, ...) {
  newx <- as.matrix(newdata)
  stopifnot(ncol(newx) == length(object$beta))
  drop(object$intercept + newx %*% object$beta)
}

# ===== Book block 2; source line 497 =====
direction_information <- c(strong = 100, weak = 1)
theta <- c(strong = 1, weak = 1)
sigma2 <- 4
lambda_demo <- 1

shrinkage <- direction_information /
  (direction_information + lambda_demo)
bias <- -lambda_demo /
  (direction_information + lambda_demo) * theta
ridge_variance <- sigma2 * direction_information /
  (direction_information + lambda_demo)^2
ols_variance <- sigma2 / direction_information

direction_table <- data.frame(
  direction = names(direction_information),
  shrinkage = unname(shrinkage),
  ols_mse = unname(ols_variance),
  ridge_squared_bias = unname(bias^2),
  ridge_variance = unname(ridge_variance),
  ridge_mse = unname(bias^2 + ridge_variance)
)
print(direction_table, digits = 6)
print(colSums(direction_table[, c("ols_mse", "ridge_mse")]))

# ===== Book block 3; source line 525 =====
set.seed(20260904)

make_known_truth_sample <- function(n, rho = 0.98, sigma = 2) {
  first_noise <- rnorm(n)
  second_noise <- rnorm(n)
  x1 <- first_noise
  x2 <- rho * first_noise + sqrt(1 - rho^2) * second_noise
  response <- 2 * x1 + 2 * x2 + rnorm(n, sd = sigma)
  data.frame(y = response, x1 = x1, x2 = x2)
}

training <- make_known_truth_sample(60)
development <- make_known_truth_sample(60)
assessment <- make_known_truth_sample(400)
lambda_grid <- c(0, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100)

candidate_fits <- lapply(
  lambda_grid,
  function(value) {
    ridge_fit(
      training[c("x1", "x2")], training$y, value
    )
  }
)
development_mse <- vapply(
  candidate_fits,
  function(fit) {
    mean(
      (development$y -
         predict(fit, development[c("x1", "x2")]))^2
    )
  },
  numeric(1)
)
selected_index <- which.min(development_mse)
selected_lambda <- lambda_grid[selected_index]
print(data.frame(lambda = lambda_grid, development_mse), digits = 6)
cat("Selected lambda from development data:", selected_lambda, "\n")

# ===== Book block 4; source line 568 =====
ols_fit <- candidate_fits[[which(lambda_grid == 0)]]
selected_fit <- candidate_fits[[selected_index]]

assessment_result <- data.frame(
  method = c("OLS", "selected ridge"),
  lambda = c(0, selected_lambda),
  training_mse = c(
    mean((training$y - predict(ols_fit, training[c("x1", "x2")]))^2),
    mean((training$y -
            predict(selected_fit, training[c("x1", "x2")]))^2)
  ),
  development_mse = c(
    development_mse[1],
    development_mse[selected_index]
  ),
  assessment_mse = c(
    mean((assessment$y -
            predict(ols_fit, assessment[c("x1", "x2")]))^2),
    mean((assessment$y -
            predict(selected_fit, assessment[c("x1", "x2")]))^2)
  ),
  coefficient_squared_error = c(
    sum((ols_fit$beta - c(2, 2))^2),
    sum((selected_fit$beta - c(2, 2))^2)
  )
)
print(assessment_result, digits = 6)
cat(
  "Assessment was read after the development choice; ",
  "this one score does not establish universal superiority.\n",
  sep = ""
)

# ===== Book block 5; source line 607 =====
data(longley, package = "datasets")
stopifnot(nrow(longley) == 16L, !anyNA(longley))

longley_x <- as.matrix(longley[setdiff(names(longley), "Employed")])
longley_y <- longley$Employed
longley_lambda <- c(0, 0.01, 0.1, 1, 10, 100, 1000)
longley_fits <- lapply(
  longley_lambda,
  function(value) ridge_fit(longley_x, longley_y, value)
)
standardized_path <- do.call(
  rbind,
  lapply(longley_fits, function(fit) fit$beta_z)
)
colnames(standardized_path) <- colnames(longley_x)
effective_df <- vapply(
  longley_fits,
  function(fit) {
    1 + sum(
      fit$singular_values^2 /
        (fit$singular_values^2 + fit$lambda)
    )
  },
  numeric(1)
)
path_summary <- data.frame(
  lambda = longley_lambda,
  effective_df = effective_df,
  coefficient_norm = sqrt(rowSums(standardized_path^2))
)
print(path_summary, digits = 6)
print(round(standardized_path, 4))
