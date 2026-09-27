# Chapter 11. Logistic Regression and Probability Predictions
# Reasoning Through Regression: Inference, Prediction, and Regularization with R
# Author: Prof. Dr. Bahadır Yüzbaşı
# Edition: 27 September 2026
# Run blocks in order in a fresh R session. See README.md.

# ===== Book block 1; source line 108 =====
eta <- c(-2, 0, 2)
probability <- plogis(eta)
odds <- probability / (1 - probability)

cbind(eta, probability, odds, recovered_eta = qlogis(probability))
stopifnot(all.equal(eta, qlogis(plogis(eta))))

# ===== Book block 2; source line 266 =====
toy <- data.frame(
  x = c(-2, -1.2, -0.5, 0.2, 0.8, 1.4, 2.1, 2.7),
  y = c(0, 0, 1, 0, 1, 1, 0, 1)
)
toy_fit <- glm(y ~ x, family = binomial(), data = toy)
new_case <- data.frame(x = 0.75)

link <- predict(toy_fit, newdata = new_case, type = "link", se.fit = TRUE)
critical <- qnorm(0.975)
link_interval <- link$fit + c(-1, 1) * critical * link$se.fit

c(
  linear_predictor = unname(link$fit),
  probability = unname(predict(toy_fit, new_case, type = "response")),
  lower_probability = plogis(link_interval[1]),
  upper_probability = plogis(link_interval[2])
)

# ===== Book block 3; source line 383 =====
brier_score <- function(y, p) mean((y - p)^2)
log_loss <- function(y, p) {
  eps <- sqrt(.Machine$double.eps)
  p_safe <- pmin(pmax(p, eps), 1 - eps)
  -mean(y * log(p_safe) + (1 - y) * log(1 - p_safe))
}
auc_pairwise <- function(y, p) {
  p_event <- p[y == 1]
  p_nonevent <- p[y == 0]
  mean(outer(
    p_event, p_nonevent,
    function(a, b) as.numeric(a > b) + 0.5 * as.numeric(a == b)
  ))
}
score_row <- function(label, y, p) data.frame(
  model = label,
  brier = brier_score(y, p),
  log_loss = log_loss(y, p),
  accuracy_0_5 = mean((p >= 0.5) == y),
  auc = auc_pairwise(y, p)
)

set.seed(20261101)
n <- 300
known <- data.frame(
  x1 = rnorm(n),
  x2 = rnorm(n),
  group = factor(rbinom(n, 1, 0.5), levels = 0:1)
)
known$eta_true <- -0.4 + 1.1 * known$x1 - 0.8 * known$x2 +
  0.6 * as.numeric(as.character(known$group))
known$p_true <- plogis(known$eta_true)
known$y <- rbinom(n, 1, known$p_true)

development <- 1:200
assessment <- 201:300
known_fit <- glm(
  y ~ x1 + x2 + group,
  family = binomial(), data = known[development, ]
)
p_model <- predict(known_fit, known[assessment, ], type = "response")
p_over <- plogis(1.75 * qlogis(p_model))
p_base <- rep(mean(known$y[development]), length(assessment))

known_scores <- rbind(
  score_row("development logistic", known$y[assessment], p_model),
  score_row("overconfident transform", known$y[assessment], p_over),
  score_row("development event-rate baseline", known$y[assessment], p_base),
  score_row("true generating probability", known$y[assessment], known$p_true[assessment])
)
known_scores

# ===== Book block 4; source line 480 =====
calibration_groups <- function(y, p, groups = 5) {
  membership <- cut(
    rank(p, ties.method = "first"),
    breaks = seq(0, length(p), length.out = groups + 1),
    include.lowest = TRUE, labels = seq_len(groups)
  )
  data.frame(
    group = seq_len(groups),
    n = as.integer(tapply(y, membership, length)),
    mean_prediction = as.numeric(tapply(p, membership, mean)),
    event_fraction = as.numeric(tapply(y, membership, mean))
  )
}
class_metrics <- function(y, p, threshold) {
  decision <- as.integer(p >= threshold)
  tp <- sum(decision == 1 & y == 1)
  fp <- sum(decision == 1 & y == 0)
  tn <- sum(decision == 0 & y == 0)
  fn <- sum(decision == 0 & y == 1)
  c(
    sensitivity = tp / (tp + fn),
    specificity = tn / (tn + fp),
    accuracy = mean(decision == y)
  )
}

y_assess <- known$y[assessment]
calibration_model <- calibration_groups(y_assess, p_model)
calibration_over <- calibration_groups(y_assess, p_over)
threshold_table <- t(vapply(
  seq(0.1, 0.9, by = 0.1),
  function(t) class_metrics(y_assess, p_model, t),
  numeric(3)
))

stopifnot(identical(p_model >= 0.5, p_over >= 0.5))
calibration_model
calibration_over
threshold_table

# ===== Book block 5; source line 561 =====
data("birthwt", package = "MASS")
birthwt_raw <- MASS::birthwt
birthwt_model <- with(birthwt_raw, data.frame(
  low = as.integer(low),
  age = age,
  lwt = lwt,
  race = factor(race, 1:3, c("white", "black", "other")),
  smoke = factor(smoke, 0:1, c("no", "yes")),
  ptl = ptl,
  ht = factor(ht, 0:1, c("no", "yes")),
  ui = factor(ui, 0:1, c("no", "yes")),
  ftv = ftv
))
stopifnot(nrow(birthwt_model) == 189, !anyNA(birthwt_model))

set.seed(20260911)
development_birthwt <- sort(c(
  sample(which(birthwt_model$low == 0),
         floor(0.75 * sum(birthwt_model$low == 0))),
  sample(which(birthwt_model$low == 1),
         floor(0.75 * sum(birthwt_model$low == 1)))
))
assessment_birthwt <- setdiff(seq_len(nrow(birthwt_model)),
                              development_birthwt)

birthwt_fit <- glm(
  low ~ age + lwt + race + smoke + ptl + ht + ui + ftv,
  family = binomial(), data = birthwt_model[development_birthwt, ]
)
p_birthwt <- predict(
  birthwt_fit, birthwt_model[assessment_birthwt, ], type = "response"
)
y_birthwt <- birthwt_model$low[assessment_birthwt]
p_birthwt_base <- rep(
  mean(birthwt_model$low[development_birthwt]),
  length(assessment_birthwt)
)

rbind(
  score_row("predeclared logistic", y_birthwt, p_birthwt),
  score_row("development event-rate baseline", y_birthwt, p_birthwt_base)
)
class_metrics(y_birthwt, p_birthwt, threshold = 0.5)
