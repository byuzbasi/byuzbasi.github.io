.validate_run_probabilities <- function(prob) {
  if (!is.atomic(prob) || !is.numeric(prob) || !is.null(dim(prob))) {
    .abort_runs_input(
      "`prob` must be a numeric vector without dimensions.",
      "prob"
    )
  }
  if (length(prob) < 1L) {
    .abort_runs_input("`prob` must contain at least one probability.", "prob")
  }
  if (anyNA(prob)) {
    .abort_runs_input("`prob` must not contain missing or NaN values.", "prob")
  }
  if (any(!is.finite(prob))) {
    .abort_runs_input("`prob` must contain only finite values.", "prob")
  }
  if (any(prob < 0 | prob > 1)) {
    .abort_runs_input("Every value in `prob` must lie in [0, 1].", "prob")
  }
  as.double(prob)
}

.validate_binary_sequence <- function(x) {
  if (!is.atomic(x) || !(is.logical(x) || is.numeric(x)) ||
      !is.null(dim(x))) {
    .abort_runs_input(
      "`x` must be a logical or numeric vector without dimensions.",
      "x"
    )
  }
  if (length(x) < 1L) {
    .abort_runs_input("`x` must contain at least one binary observation.", "x")
  }
  if (anyNA(x)) {
    .abort_runs_input("`x` must not contain missing or NaN values.", "x")
  }
  x_numeric <- as.double(x)
  if (any(!is.finite(x_numeric)) || any(!(x_numeric %in% c(0, 1)))) {
    .abort_runs_input("`x` must contain only 0 and 1 values.", "x")
  }
  as.integer(x_numeric)
}

