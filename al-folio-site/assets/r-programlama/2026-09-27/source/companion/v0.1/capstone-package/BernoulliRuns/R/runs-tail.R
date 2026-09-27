#' Exact One-Sided Tail Probability for the Run Count
#'
#' Computes the inclusive lower or upper tail probability of the observed run
#' count under mutually independent Bernoulli trials with fixed, supplied
#' success probabilities.
#'
#' @param x A non-empty logical or numeric vector containing only zeroes and
#'   ones. It is the observed binary sequence.
#' @param prob A numeric vector of the same length as `x`. Its `i`th element is
#'   the success probability of the `i`th trial and must lie in `[0, 1]`.
#' @param tail A character string selecting the inclusive `"lower"` tail,
#'   \eqn{P(R \le r_{obs})}, or inclusive `"upper"` tail,
#'   \eqn{P(R \ge r_{obs})}. Partial matching follows [match.arg()].
#'
#' @return An object of class `runs_exact_tail`, a list with components
#'   `statistic`, `p.value`, `alternative`, `method`, and `probabilities`.
#'
#' @details
#' The result is a conditional probability under the supplied model. If
#' `prob` was estimated from the same observations, the result is not by
#' itself a calibrated exact test. The observed point is included in either
#' tail. The package deliberately does not define a two-sided p-value.
#'
#' @export
#'
#' @examples
#' x <- c(0, 1, 1, 0)
#' prob <- c(0.15, 0.40, 0.75, 0.60)
#' runs_tail(x, prob, tail = "upper")
runs_tail <- function(x, prob, tail = c("lower", "upper")) {
  tail <- match.arg(tail)
  x <- .validate_binary_sequence(x)
  prob <- .validate_run_probabilities(prob)
  if (length(x) != length(prob)) {
    .abort_runs_input("`x` and `prob` must have the same length.", "x")
  }

  observed <- count_runs(x)
  pmf <- .runs_pmf(prob)
  probability <- if (tail == "lower") {
    sum(pmf[seq_len(observed)])
  } else {
    sum(pmf[observed:length(pmf)])
  }

  structure(
    list(
      statistic = c(runs = observed),
      p.value = unname(probability),
      alternative = paste(tail, "one-sided tail"),
      method = "Exact run-count distribution for independent Bernoulli trials",
      probabilities = prob
    ),
    class = "runs_exact_tail"
  )
}

