# Bölüm 22: küçük n için tam sayım ve sözleşme odaklı test tasarımı.

project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  stop("RBOOK_PROJECT_DIR zorunludur.", call. = FALSE)
}
project_dir <- normalizePath(project_dir, mustWork = TRUE)

if (!requireNamespace("testthat", quietly = TRUE)) {
  stop("Kurulu testthat paketi gereklidir; otomatik kurulum yapılmadı.",
       call. = FALSE)
}
testthat::local_edition(3)

prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
prototype_environment <- new.env(parent = baseenv())
sys.source(prototype_path, envir = prototype_environment, keep.source = TRUE)

count_runs_reference <- get(
  "count_runs_reference", envir = prototype_environment, inherits = FALSE
)
runs_pmf_reference <- get(
  "runs_pmf_reference", envir = prototype_environment, inherits = FALSE
)
runs_mean_reference <- get(
  "runs_mean_reference", envir = prototype_environment, inherits = FALSE
)
runs_tail_reference <- get(
  "runs_tail_reference", envir = prototype_environment, inherits = FALSE
)

enumerate_runs_pmf <- function(prob) {
  n <- length(prob)
  grid <- expand.grid(
    rep(list(c(0L, 1L)), n),
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  sequences <- as.matrix(grid)
  storage.mode(sequences) <- "integer"

  weights <- apply(sequences, 1L, function(x) {
    prod(ifelse(x == 1L, prob, 1 - prob))
  })
  run_counts <- apply(sequences, 1L, count_runs_reference)
  pmf <- numeric(n)
  for (r in seq_len(n)) {
    pmf[r] <- sum(weights[run_counts == r])
  }
  names(pmf) <- as.character(seq_len(n))
  pmf
}

# 1e-12 yalnız n <= 8 tam sayım duman sınaması içindir. Genel kullanıcı
# toleransı, bilimsel varsayılan veya üretim doğruluğu iddiası değildir.
smoke_tolerance <- 1e-12
enumeration_summary <- data.frame(
  n = seq_len(8L),
  sequences = 2^(seq_len(8L)),
  max_absolute_difference = NA_real_,
  mass_error = NA_real_,
  mean_error = NA_real_
)

for (n in seq_len(8L)) {
  prob <- seq(0.12, 0.88, length.out = n)
  exact <- runs_pmf_reference(prob)
  enumerated <- enumerate_runs_pmf(prob)
  pmf_mean <- sum(seq_len(n) * exact)
  analytic_mean <- runs_mean_reference(prob)

  enumeration_summary$max_absolute_difference[n] <- max(abs(
    exact - enumerated
  ))
  enumeration_summary$mass_error[n] <- abs(sum(exact) - 1)
  enumeration_summary$mean_error[n] <- abs(pmf_mean - analytic_mean)

  testthat::expect_equal(exact, enumerated, tolerance = smoke_tolerance)
  testthat::expect_equal(sum(exact), 1, tolerance = smoke_tolerance)
  testthat::expect_equal(
    pmf_mean, analytic_mean, tolerance = smoke_tolerance
  )
  testthat::expect_true(all(exact >= -smoke_tolerance))
}

testthat::expect_equal(
  runs_pmf_reference(c(0, 0, 0)),
  c("1" = 1, "2" = 0, "3" = 0),
  tolerance = smoke_tolerance
)
testthat::expect_equal(
  runs_pmf_reference(c(0, 1, 0)),
  c("1" = 0, "2" = 0, "3" = 1),
  tolerance = smoke_tolerance
)

invalid_error <- tryCatch(
  {
    runs_pmf_reference(c(0.2, 1.2))
    NULL
  },
  error = function(cnd) cnd
)
testthat::expect_s3_class(invalid_error, "runs_input_error")
testthat::expect_identical(invalid_error$argument, "prob")

prob <- c(0.15, 0.40, 0.75, 0.60)
prob_before <- prob
observed <- c(0L, 1L, 1L, 0L)
lower <- runs_tail_reference(observed, prob, tail = "lower")$p.value
upper <- runs_tail_reference(observed, prob, tail = "upper")$p.value
observed_runs <- count_runs_reference(observed)
pmf <- runs_pmf_reference(prob)
testthat::expect_equal(
  unname(lower + upper - pmf[observed_runs]),
  1,
  tolerance = smoke_tolerance
)
testthat::expect_identical(prob, prob_before)

ch22_result <- all(
  enumeration_summary$max_absolute_difference <= smoke_tolerance,
  enumeration_summary$mass_error <= smoke_tolerance,
  enumeration_summary$mean_error <= smoke_tolerance
)
if (!isTRUE(ch22_result)) {
  stop("Bölüm 22 test tasarımı denetimi başarısız.", call. = FALSE)
}

cat("Bölüm 22: n=1,...,8 tam sayım ve sözleşme testleri geçti.\n")
