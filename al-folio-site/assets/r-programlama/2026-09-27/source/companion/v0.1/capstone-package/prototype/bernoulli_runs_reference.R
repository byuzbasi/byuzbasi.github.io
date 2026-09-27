# Yaşayan paket için saf-R bilimsel referans prototipi.
#
# Bu dosya bir R paketi değildir. Paket adı ve lisansı onaylanana kadar
# DESCRIPTION/NAMESPACE veya yayımlama metadata'sı oluşturulmaz.

new_runs_input_error <- function(message, argument) {
  structure(
    list(message = message, call = NULL, argument = argument),
    class = c("runs_input_error", "error", "condition")
  )
}

abort_runs_input <- function(message, argument) {
  stop(new_runs_input_error(message, argument))
}

validate_run_probabilities <- function(prob) {
  if (!is.atomic(prob) || !is.numeric(prob) || !is.null(dim(prob))) {
    abort_runs_input("`prob` boyutsuz bir sayısal vektör olmalıdır.", "prob")
  }
  if (length(prob) < 1L) {
    abort_runs_input("`prob` en az bir olasılık içermelidir.", "prob")
  }
  if ((anyNA(prob))) {
    abort_runs_input("`prob` eksik veya NaN değer içeremez.", "prob")
  }
  if (any(!is.finite(prob))) {
    abort_runs_input("`prob` yalnızca sonlu değerler içermelidir.", "prob")
  }
  if (any(prob < 0 | prob > 1)) {
    abort_runs_input("`prob` değerleri kapalı [0, 1] aralığında olmalıdır.",
                     "prob")
  }
  as.double(prob)
}

validate_binary_sequence <- function(x) {
  if (!is.atomic(x) || !(is.logical(x) || is.numeric(x)) ||
      !is.null(dim(x))) {
    abort_runs_input("`x` boyutsuz mantıksal veya sayısal vektör olmalıdır.",
                     "x")
  }
  if (length(x) < 1L) {
    abort_runs_input("`x` en az bir ikili gözlem içermelidir.", "x")
  }
  if (anyNA(x)) {
    abort_runs_input("`x` eksik veya NaN değer içeremez.", "x")
  }
  x_numeric <- as.double(x)
  if (any(!is.finite(x_numeric)) || any(!(x_numeric %in% c(0, 1)))) {
    abort_runs_input("`x` yalnızca 0 ve 1 değerlerini içermelidir.", "x")
  }
  as.integer(x_numeric)
}

count_runs_reference <- function(x) {
  x <- validate_binary_sequence(x)
  n <- length(x)
  if (n == 1L) {
    return(1L)
  }
  as.integer(1L + sum(x[-1L] != x[-n]))
}

runs_pmf_reference <- function(prob) {
  prob <- validate_run_probabilities(prob)
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

runs_distribution_reference <- function(prob) {
  pmf <- runs_pmf_reference(prob)
  data.frame(
    runs = seq_along(pmf),
    probability = unname(pmf),
    cumulative = cumsum(unname(pmf)),
    stringsAsFactors = FALSE
  )
}

runs_mean_reference <- function(prob) {
  prob <- validate_run_probabilities(prob)
  n <- length(prob)
  if (n == 1L) {
    return(1)
  }
  previous <- prob[-n]
  current <- prob[-1L]
  1 + sum(previous * (1 - current) + (1 - previous) * current)
}

runs_tail_reference <- function(x, prob, tail = c("lower", "upper")) {
  tail <- match.arg(tail)
  x <- validate_binary_sequence(x)
  prob <- validate_run_probabilities(prob)
  if (length(x) != length(prob)) {
    abort_runs_input("`x` ve `prob` aynı uzunlukta olmalıdır.", "x")
  }

  observed <- count_runs_reference(x)
  pmf <- runs_pmf_reference(prob)
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

