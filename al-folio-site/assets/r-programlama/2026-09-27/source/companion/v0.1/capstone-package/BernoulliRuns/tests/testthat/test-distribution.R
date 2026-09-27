testthat::test_that("distribution has the documented schema and unit mass", {
  distribution <- runs_distribution(c(0.15, 0.40, 0.75, 0.60))

  testthat::expect_s3_class(distribution, "data.frame")
  testthat::expect_identical(
    names(distribution),
    c("runs", "probability", "cumulative")
  )
  testthat::expect_identical(distribution$runs, 1:4)
  testthat::expect_equal(sum(distribution$probability), 1, tolerance = 1e-12)
  testthat::expect_equal(tail(distribution$cumulative, 1L), 1,
                         tolerance = 1e-12)
  testthat::expect_true(all(distribution$probability >= 0))
})

testthat::test_that("dynamic programming agrees with exhaustive enumeration", {
  tolerance <- 1e-12
  for (n in seq_len(8L)) {
    prob <- seq(0.12, 0.88, length.out = n)
    actual <- runs_distribution(prob)$probability
    enumerated <- enumerate_runs_pmf(prob)

    testthat::expect_equal(actual, enumerated, tolerance = tolerance)
    testthat::expect_equal(sum(actual), 1, tolerance = tolerance)
    testthat::expect_equal(
      sum(seq_len(n) * actual),
      runs_mean(prob),
      tolerance = tolerance
    )
  }
})

testthat::test_that("degenerate probability vectors remain exact", {
  testthat::expect_equal(
    runs_distribution(c(0, 0, 0))$probability,
    c(1, 0, 0),
    tolerance = 1e-12
  )
  testthat::expect_equal(
    runs_distribution(c(0, 1, 0))$probability,
    c(0, 0, 1),
    tolerance = 1e-12
  )
  testthat::expect_equal(runs_mean(0.25), 1)
})

testthat::test_that("invalid probabilities raise classed errors", {
  invalid_probabilities <- list(
    numeric(), c(0.2, NA_real_), c(0.2, NaN), c(0.2, Inf),
    c(-0.1, 0.2), c(0.2, 1.1), matrix(c(0.2, 0.8), nrow = 1L),
    c(TRUE, FALSE)
  )
  for (prob in invalid_probabilities) {
    error <- tryCatch(runs_distribution(prob), error = identity)
    testthat::expect_s3_class(error, "runs_input_error")
    testthat::expect_identical(error$argument, "prob")
  }
})

testthat::test_that("distribution calculation has no caller-visible side effects", {
  prob <- c(0.10, 0.45, 0.80, 0.35)
  prob_before <- prob
  options_before <- options()
  working_directory_before <- getwd()
  seed_existed_before <- exists(".Random.seed", .GlobalEnv, inherits = FALSE)
  seed_before <- if (seed_existed_before) .GlobalEnv$.Random.seed else NULL

  invisible(runs_distribution(prob))

  seed_existed_after <- exists(".Random.seed", .GlobalEnv, inherits = FALSE)
  seed_after <- if (seed_existed_after) .GlobalEnv$.Random.seed else NULL
  testthat::expect_identical(prob, prob_before)
  testthat::expect_identical(options(), options_before)
  testthat::expect_identical(getwd(), working_directory_before)
  testthat::expect_identical(seed_existed_after, seed_existed_before)
  if (seed_existed_before) {
    testthat::expect_identical(seed_after, seed_before)
  }
})

