testthat::test_that("count_runs counts maximal equal-value blocks", {
  testthat::expect_identical(count_runs(0), 1L)
  testthat::expect_identical(count_runs(c(FALSE, TRUE, TRUE, FALSE)), 3L)
  testthat::expect_identical(count_runs(c(0, 0, 1, 1, 0)), 3L)
  testthat::expect_identical(count_runs(c(0, 1, 0, 1)), 4L)
})

testthat::test_that("count_runs rejects values outside the binary contract", {
  invalid_inputs <- list(
    numeric(), c(0, 2), c(0, NA_real_), c(0, Inf),
    matrix(c(0, 1), nrow = 1L), "01"
  )
  for (input in invalid_inputs) {
    error <- tryCatch(count_runs(input), error = identity)
    testthat::expect_s3_class(error, "runs_input_error")
    testthat::expect_identical(error$argument, "x")
  }
})

