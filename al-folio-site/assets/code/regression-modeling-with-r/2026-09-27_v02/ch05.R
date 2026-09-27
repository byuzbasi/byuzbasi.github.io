# Chapter 5. Model Checking and Assumption Failures
# Regression Modeling with R: Inference, Prediction, and Regularization
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 285 =====
sets <- lapply(seq_len(4), function(j) {
  data.frame(
    row = seq_len(nrow(anscombe)),
    x = anscombe[[paste0("x", j)]],
    y = anscombe[[paste0("y", j)]]
  )
})
fits <- lapply(sets, function(dat) {
  lm(y ~ x, data = dat, na.action = na.fail)
})
stopifnot(length(fits) == 4L,
          all(vapply(fits, nobs, integer(1)) == 11L))

# ===== Book block 2; source line 304 =====
summary_rows <- lapply(seq_along(fits), function(j) {
  dat <- sets[[j]]
  fit <- fits[[j]]
  c(set = j, mean_x = mean(dat$x), mean_y = mean(dat$y),
    var_x = var(dat$x), var_y = var(dat$y),
    correlation = cor(dat$x, dat$y),
    intercept = unname(coef(fit)[1]),
    slope = unname(coef(fit)[2]),
    SSE = deviance(fit),
    R2 = summary(fit)$r.squared)
})
summary_table <- do.call(rbind, summary_rows)
round(summary_table, 6)

# ===== Book block 3; source line 324 =====
fit3 <- fits[[3]]
X3 <- model.matrix(fit3)
y3 <- model.response(model.frame(fit3))
H3 <- X3 %*% solve(crossprod(X3), t(X3))
e3 <- drop((diag(nrow(X3)) - H3) %*% y3)
s3 <- summary(fit3)$sigma
h3 <- diag(H3)
r3_hand <- e3 / (s3 * sqrt(1 - h3))
D3_hand <- (r3_hand^2 / ncol(X3)) * h3 / (1 - h3)
stopifnot(all.equal(e3, residuals(fit3), tolerance = 1e-10),
          all.equal(h3, hatvalues(fit3), tolerance = 1e-10),
          all.equal(r3_hand, rstandard(fit3), tolerance = 1e-10),
          all.equal(D3_hand, cooks.distance(fit3), tolerance = 1e-10))
data.frame(row = sets[[3]]$row, residual = e3,
           leverage = h3, standardized = r3_hand,
           cook = D3_hand)

# ===== Book block 4; source line 347 =====
i <- 3L
fit3_minus_i <- lm(y ~ x, data = sets[[3]][-i, ], na.action = na.fail)
deleted_direct <- sets[[3]]$y[i] -
  predict(fit3_minus_i, newdata = sets[[3]][i, , drop = FALSE])
deleted_formula <- residuals(fit3)[i] / (1 - hatvalues(fit3)[i])

fit4 <- fits[[4]]
h4 <- hatvalues(fit4)
rank_without_8 <- qr(model.matrix(fit4)[-8, , drop = FALSE])$rank
c(deleted_direct = deleted_direct,
  deleted_formula = deleted_formula,
  set4_row8_leverage = h4[8],
  rank_without_set4_row8 = rank_without_8)

# ===== Book block 5; source line 367 =====
old_par <- par(no.readonly = TRUE)
par(mfrow = c(2, 2))
plot(fits[[2]], which = 1, id.n = 0,
     main = "Set II: residuals versus fitted")
plot(fits[[2]], which = 3, id.n = 0,
     main = "Set II: scale-location")
plot(fits[[3]], which = 2, id.n = 1,
     main = "Set III: normal Q-Q")
plot(fits[[3]], which = 5, id.n = 1,
     main = "Set III: residuals versus leverage")
par(old_par)
