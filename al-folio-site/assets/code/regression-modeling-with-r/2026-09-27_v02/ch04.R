# Chapter 4. Uncertainty, Inference, and Prediction Intervals
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 407 =====
toy <- data.frame(x = c(1, 2, 3, 4),
                  z = c(1, 2, 4, 3),
                  y = c(4, 8, 6, 10))
fit <- lm(y ~ x, data = toy, na.action = na.fail)
X <- model.matrix(fit)
nu <- df.residual(fit)
s2 <- sum(residuals(fit)^2) / nu
c(n = nrow(X), p = ncol(X), df = nu, s2 = s2)

# ===== Book block 2; source line 422 =====
C <- solve(crossprod(X))
V_hand <- s2 * C
V_hand
vcov(fit)
sqrt(diag(V_hand))
coef(summary(fit))

# ===== Book block 3; source line 437 =====
level <- 0.95
alpha <- 1 - level
q <- qt(1 - alpha / 2, df = nu)
b1 <- unname(coef(fit)["x"])
se1 <- sqrt(V_hand["x", "x"])
ci_hand <- b1 + c(-1, 1) * q * se1
ci_hand
confint(fit, parm = "x", level = level)
t_obs <- b1 / se1
c(t = t_obs,
  p_two_sided = 2 * pt(abs(t_obs), df = nu,
                      lower.tail = FALSE))

# ===== Book block 4; source line 456 =====
new_x <- data.frame(x = c(2.5, 5))
mean_ci <- predict(fit, newdata = new_x,
                   interval = "confidence", level = level)
individual_pi <- predict(fit, newdata = new_x,
                         interval = "prediction", level = level)
h <- 1 / nrow(toy) + (new_x$x - mean(toy$x))^2 /
     sum((toy$x - mean(toy$x))^2)
cbind(new_x, h, mean_ci)
individual_pi
cbind(mean_se = sqrt(s2 * h),
      prediction_se = sqrt(s2 * (1 + h)))

# ===== Book block 5; source line 474 =====
full <- lm(y ~ x + z, data = toy, na.action = na.fail)
rx <- residuals(lm(x ~ z, data = toy, na.action = na.fail))
ry <- residuals(lm(y ~ z, data = toy, na.action = na.fail))
naive <- lm(ry ~ rx, na.action = na.fail)
c(full_x = unname(coef(full)["x"]),
  partial_x = unname(coef(naive)["rx"]))
c(full_df = df.residual(full),
  naive_df = df.residual(naive))
c(full_se = sqrt(vcov(full)["x", "x"]),
  naive_se = sqrt(vcov(naive)["rx", "rx"]))
