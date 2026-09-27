#' Print an Exact Run-Count Tail Result
#'
#' @param x An object returned by [runs_tail()].
#' @param digits The number of significant digits used for displayed values.
#' @param ... Additional arguments reserved for future methods.
#'
#' @return `x`, invisibly.
#' @export
print.runs_exact_tail <- function(
    x,
    digits = max(3L, getOption("digits") - 3L),
    ...
) {
  cat("\n", x$method, "\n\n", sep = "")
  cat("number of runs =", format(unname(x$statistic), digits = digits), "\n")
  cat("p-value =", format.pval(x$p.value, digits = digits), "\n")
  cat("alternative hypothesis:", x$alternative, "\n\n")
  invisible(x)
}

