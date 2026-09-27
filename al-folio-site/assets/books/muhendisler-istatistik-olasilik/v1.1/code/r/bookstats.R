book_mean <- function(x) {
  stopifnot(length(x) >= 1L, all(is.finite(x)))
  sum(x) / length(x)
}

book_sample_variance <- function(x) {
  stopifnot(length(x) >= 2L, all(is.finite(x)))
  center <- book_mean(x)
  sum((x - center)^2) / (length(x) - 1L)
}

posterior_defect <- function(prevalence, sensitivity, specificity) {
  values <- c(prevalence, sensitivity, specificity)
  stopifnot(all(values >= 0), all(values <= 1))
  true_alarm <- sensitivity * prevalence
  false_alarm <- (1 - specificity) * (1 - prevalence)
  denominator <- true_alarm + false_alarm
  stopifnot(denominator > 0)
  true_alarm / denominator
}

series_reliability <- function(component_reliabilities) {
  stopifnot(length(component_reliabilities) >= 1L)
  stopifnot(all(component_reliabilities >= 0), all(component_reliabilities <= 1))
  prod(component_reliabilities)
}

parallel_reliability <- function(component_reliabilities) {
  stopifnot(length(component_reliabilities) >= 1L)
  stopifnot(all(component_reliabilities >= 0), all(component_reliabilities <= 1))
  1 - prod(1 - component_reliabilities)
}
