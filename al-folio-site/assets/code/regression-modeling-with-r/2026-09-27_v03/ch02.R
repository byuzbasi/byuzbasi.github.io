# Chapter 2. Simple Linear Regression
# Reasoning Through Regression: Inference, Prediction, and Regularization with R
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 320 =====
toy <- data.frame(x = c(1, 2, 3, 4),
                  y = c(4, 8, 6, 10))
xbar <- mean(toy$x)
ybar <- mean(toy$y)
u <- toy$x - xbar
v <- toy$y - ybar
Sxx <- sum(u^2)
Sxy <- sum(u * v)
b1_hand <- Sxy / Sxx
b0_hand <- ybar - b1_hand * xbar
c(intercept = b0_hand, slope = b1_hand)

# ===== Book block 2; source line 340 =====
fit <- lm(y ~ x, data = toy, na.action = na.fail)
coef(fit)
yhat <- fitted(fit)
e <- residuals(fit)
data.frame(toy, fitted = yhat, residual = e)

# ===== Book block 3; source line 354 =====
sse <- sum(e^2)
sst <- sum(v^2)
ssr <- sum((yhat - ybar)^2)
c(sum_e = sum(e), sum_xe = sum(toy$x * e))
c(SSE = sse, SST = sst, SSR = ssr,
  R_squared = 1 - sse / sst)

# ===== Book block 4; source line 369 =====
new_x <- data.frame(x = c(2.5, 5))
predict(fit, newdata = new_x)
