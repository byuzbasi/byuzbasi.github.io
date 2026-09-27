#' Count Runs in a Binary Sequence
#'
#' Counts maximal consecutive blocks of equal values in a non-empty binary
#' sequence. For example, `00110` contains the runs `00`, `11`, and `0`.
#'
#' @param x A non-empty logical or numeric vector containing only zeroes and
#'   ones. Missing and non-finite values are not allowed.
#'
#' @return A scalar integer giving the number of runs in `x`.
#' @export
#'
#' @examples
#' count_runs(c(0, 0, 1, 1, 0))
count_runs <- function(x) {
  x <- .validate_binary_sequence(x)
  n <- length(x)
  if (n == 1L) {
    return(1L)
  }
  as.integer(1L + sum(x[-1L] != x[-n]))
}

.runs_pmf <- function(prob) {
  prob <- .validate_run_probabilities(prob)
  n <- length(prob)

  end_zero <- numeric(n)
  end_one <- numeric(n)
  end_zero[1L] <- 1 - prob[1L]
  end_one[1L] <- prob[1L]

  if (n > 1L) {
    for (i in 2L:n) {
      previous <- seq_len(i - 1L)
      current <- seq_len(i)
      new_zero <- numeric(n)
      new_one <- numeric(n)

      new_zero[previous] <- new_zero[previous] +
        (1 - prob[i]) * end_zero[previous]
      new_zero[previous + 1L] <- new_zero[previous + 1L] +
        (1 - prob[i]) * end_one[previous]
      new_one[previous] <- new_one[previous] +
        prob[i] * end_one[previous]
      new_one[previous + 1L] <- new_one[previous + 1L] +
        prob[i] * end_zero[previous]

      end_zero[current] <- new_zero[current]
      end_one[current] <- new_one[current]
    }
  }

  pmf <- end_zero + end_one
  names(pmf) <- as.character(seq_len(n))
  pmf
}

#' Exact Distribution of the Total Run Count
#'
#' Computes the exact probability mass and cumulative distribution of the
#' total number of runs in mutually independent Bernoulli trials. The trials
#' need not have a common success probability. The supplied probabilities are
#' treated as fixed and known; this function performs no estimation.
#'
#' @param prob A non-empty numeric vector. Its `i`th element is the success
#'   probability of the `i`th Bernoulli trial and must be finite and in the
#'   closed interval `[0, 1]`.
#'
#' @return A data frame with one row for every possible run count and columns:
#'   \describe{
#'   \item{`runs`}{The possible total run counts from 1 to `length(prob)`.}
#'   \item{`probability`}{The exact probability mass at each run count.}
#'   \item{`cumulative`}{The inclusive lower cumulative probability.}
#'   }
#'
#' @details
#' The calculation uses a finite-state dynamic program indexed by the number
#' of observations processed, the current run count, and the last binary
#' value. Its time complexity is quadratic and its working memory is linear
#' in `length(prob)`.
#'
#' @references
#' Fu, J. C. and Koutras, M. V. (1994). Distribution theory of runs: A Markov
#' chain approach. *Journal of the American Statistical Association*, 89(427),
#' 1050--1058. \doi{10.1080/01621459.1994.10476841}.
#'
#' @export
#'
#' @examples
#' runs_distribution(c(0.15, 0.40, 0.75, 0.60))
runs_distribution <- function(prob) {
  pmf <- .runs_pmf(prob)
  data.frame(
    runs = seq_along(pmf),
    probability = unname(pmf),
    cumulative = cumsum(unname(pmf)),
    stringsAsFactors = FALSE
  )
}

#' Expected Total Number of Runs
#'
#' Computes the exact expected total run count for mutually independent
#' Bernoulli trials whose success probabilities may vary by position.
#'
#' @inheritParams runs_distribution
#'
#' @return A scalar double giving the expected number of runs.
#'
#' @details
#' The expectation is one plus the sum of the probabilities that successive
#' observations differ. It is conditional on the supplied probabilities and
#' the mutual-independence assumption.
#'
#' @export
#'
#' @examples
#' runs_mean(c(0.15, 0.40, 0.75, 0.60))
runs_mean <- function(prob) {
  prob <- .validate_run_probabilities(prob)
  n <- length(prob)
  if (n == 1L) {
    return(1)
  }
  previous <- prob[-n]
  current <- prob[-1L]
  1 + sum(previous * (1 - current) + (1 - previous) * current)
}

