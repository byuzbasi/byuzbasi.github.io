# Chapter 3. Multiple Regression and Conditional Interpretation
# Reasoning Through Regression: Inference, Prediction, and Regularization with R
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 402 =====
toy <- data.frame(x = c(1, 2, 3, 4),
                  z = c(1, 2, 4, 3),
                  y = c(4, 8, 6, 10))
fit <- lm(y ~ x + z, data = toy, na.action = na.fail)
X <- model.matrix(fit)
X
c(n = nrow(X), p = ncol(X), rank = qr(X)$rank)
coef(fit)

# ===== Book block 2; source line 419 =====
b_qr <- qr.solve(X, toy$y)
yhat <- fitted(fit)
e <- residuals(fit)
cbind(toy, fitted = yhat, residual = e)
drop(X %*% coef(fit))
b_qr
crossprod(X, e)
c(SSE = sum(e^2),
  R_squared = 1 - sum(e^2) / sum((toy$y - mean(toy$y))^2))

# ===== Book block 3; source line 439 =====
simple <- lm(y ~ x, data = toy, na.action = na.fail)
z_on_x <- lm(z ~ x, data = toy, na.action = na.fail)
c(simple_x = unname(coef(simple)["x"]),
  adjusted_x = unname(coef(fit)["x"]),
  identity = unname(coef(fit)["x"] +
    coef(fit)["z"] * coef(z_on_x)["x"]))
c(simple_SSE = sum(residuals(simple)^2),
  multiple_SSE = sum(e^2))

# ===== Book block 4; source line 456 =====
aux_x <- lm(x ~ z, data = toy, na.action = na.fail)
aux_y <- lm(y ~ z, data = toy, na.action = na.fail)
rx <- residuals(aux_x)
ry <- residuals(aux_y)
b_partial <- sum(rx * ry) / sum(rx^2)
cbind(rx, ry, full_residual = e,
      partial_residual = ry - b_partial * rx)
c(partial_slope = b_partial,
  full_x_slope = unname(coef(fit)["x"]))

# ===== Book block 5; source line 474 =====
new_points <- data.frame(x = c(2.5, 1), z = c(2.5, 4))
cbind(new_points,
      point_prediction = predict(fit, newdata = new_points))
