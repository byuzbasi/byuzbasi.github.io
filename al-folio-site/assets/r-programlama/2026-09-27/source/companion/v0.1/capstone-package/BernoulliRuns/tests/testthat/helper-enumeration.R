enumerate_runs_pmf <- function(prob) {
  n <- length(prob)
  grid <- expand.grid(
    rep(list(c(0L, 1L)), n),
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  sequences <- as.matrix(grid)
  storage.mode(sequences) <- "integer"

  count_independently <- function(x) {
    if (length(x) == 1L) {
      return(1L)
    }
    1L + sum(x[-1L] != x[-length(x)])
  }
  weights <- apply(sequences, 1L, function(x) {
    prod(ifelse(x == 1L, prob, 1 - prob))
  })
  run_counts <- apply(sequences, 1L, count_independently)
  vapply(seq_len(n), function(r) {
    sum(weights[run_counts == r])
  }, numeric(1))
}

