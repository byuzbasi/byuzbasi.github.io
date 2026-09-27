#' BernoulliRuns: Exact Run-Count Distributions
#'
#' `BernoulliRuns` computes the exact distribution of the total number of
#' runs in a non-empty sequence of mutually independent Bernoulli trials.
#' The success probability may differ at every position and is treated as
#' known input. The package also counts observed runs, evaluates the expected
#' run count, and computes inclusive lower or upper one-sided tail
#' probabilities.
#'
#' A run is a maximal consecutive block of equal binary values. The package
#' does not estimate success probabilities, model dependent observations, or
#' define a two-sided p-value.
#'
#' @references
#' Fu, J. C. and Koutras, M. V. (1994). Distribution theory of runs: A Markov
#' chain approach. *Journal of the American Statistical Association*, 89(427),
#' 1050--1058. \doi{10.1080/01621459.1994.10476841}.
#'
#' @keywords internal
"_PACKAGE"

