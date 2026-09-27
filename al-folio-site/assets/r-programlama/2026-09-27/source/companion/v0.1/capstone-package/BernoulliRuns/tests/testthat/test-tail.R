testthat::test_that("one-sided tails are inclusive", {
  x <- c(0L, 1L, 1L, 0L)
  prob <- c(0.15, 0.40, 0.75, 0.60)
  observed <- count_runs(x)
  mass <- runs_distribution(prob)$probability[observed]
  lower <- runs_tail(x, prob, tail = "lower")
  upper <- runs_tail(x, prob, tail = "upper")

  testthat::expect_s3_class(lower, "runs_exact_tail")
  testthat::expect_identical(unname(lower$statistic), observed)
  testthat::expect_equal(
    lower$p.value + upper$p.value - mass,
    1,
    tolerance = 1e-12
  )
  testthat::expect_identical(lower$probabilities, prob)
})

testthat::test_that("tail inputs retain the scientific contract", {
  mismatch <- tryCatch(
    runs_tail(c(0, 1), c(0.2, 0.4, 0.6)),
    error = identity
  )
  testthat::expect_s3_class(mismatch, "runs_input_error")
  testthat::expect_identical(mismatch$argument, "x")
  testthat::expect_error(
    runs_tail(c(0, 1), c(0.2, 0.4), tail = "two-sided"),
    "one of"
  )
})

testthat::test_that("tail results have a stable print method", {
  result <- runs_tail(c(0, 1, 1, 0), c(0.15, 0.40, 0.75, 0.60))
  output <- utils::capture.output(returned <- print(result))

  testthat::expect_identical(returned, result)
  testthat::expect_true(any(grepl("number of runs", output, fixed = TRUE)))
  testthat::expect_true(any(grepl("p-value", output, fixed = TRUE)))
})

