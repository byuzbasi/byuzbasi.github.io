nearly_equal_demo <- function(a, b, absolute_tolerance, relative_tolerance) {
  values <- c(a, b, absolute_tolerance, relative_tolerance)
  if (!is.numeric(values) || length(a) != 1L || length(b) != 1L ||
      length(absolute_tolerance) != 1L || length(relative_tolerance) != 1L ||
      anyNA(values) || any(!is.finite(values))) {
    stop("Bütün girdiler sonlu sayısal skalerler olmalıdır.", call. = FALSE)
  }
  if (absolute_tolerance < 0 || relative_tolerance < 0) {
    stop("Toleranslar negatif olamaz.", call. = FALSE)
  }
  absolute_error <- abs(a - b)
  permitted_error <- absolute_tolerance +
    relative_tolerance * max(abs(a), abs(b))
  absolute_error <= permitted_error
}

floating_sum <- 0.1 + 0.2
floating_target <- 0.3
floating_exact_comparison <- identical(floating_sum, floating_target)
floating_toleranced_comparison <- nearly_equal_demo(
  floating_sum,
  floating_target,
  absolute_tolerance = 1e-15,
  relative_tolerance = 1e-15
)

A <- matrix(c(4, 1, 2, 3), nrow = 2L, byrow = TRUE)
b <- c(1, 2)
linear_solution <- solve(A, b)
linear_residual <- as.vector(A %*% linear_solution - b)
linear_residual_norm <- sqrt(sum(linear_residual^2))
matrix_condition_number <- kappa(A, exact = TRUE)

quadratic_objective <- function(theta) {
  if (!is.numeric(theta) || length(theta) != 1L ||
      anyNA(theta) || !is.finite(theta)) {
    stop("`theta` sonlu sayısal bir skaler olmalıdır.", call. = FALSE)
  }
  (theta - 2)^2 + 1
}
optimization <- stats::optim(
  par = 0,
  fn = quadratic_objective,
  method = "BFGS"
)

run_stream_demo <- function(seed = 20260906L) {
  if (!is.numeric(seed) || length(seed) != 1L || anyNA(seed) ||
      !is.finite(seed)) {
    stop("`seed` tek ve sonlu bir sayı olmalıdır.", call. = FALSE)
  }

  old_kind <- RNGkind()
  old_seed_exists <- exists(".Random.seed", envir = .GlobalEnv,
                            inherits = FALSE)
  old_seed <- if (old_seed_exists) {
    get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  } else {
    NULL
  }
  on.exit({
    do.call(RNGkind, as.list(old_kind))
    if (old_seed_exists) {
      assign(".Random.seed", old_seed, envir = .GlobalEnv)
    } else if (exists(".Random.seed", envir = .GlobalEnv,
                      inherits = FALSE)) {
      rm(".Random.seed", envir = .GlobalEnv)
    }
  }, add = TRUE)

  RNGkind(
    kind = "L'Ecuyer-CMRG",
    normal.kind = "Inversion",
    sample.kind = "Rejection"
  )
  set.seed(as.integer(seed))
  root_state <- get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  second_state <- parallel::nextRNGStream(root_state)

  assign(".Random.seed", root_state, envir = .GlobalEnv)
  stream_one <- stats::runif(4L)
  assign(".Random.seed", second_state, envir = .GlobalEnv)
  stream_two <- stats::runif(4L)

  assign(".Random.seed", root_state, envir = .GlobalEnv)
  repeated_one <- stats::runif(4L)
  assign(".Random.seed", second_state, envir = .GlobalEnv)
  repeated_two <- stats::runif(4L)

  list(
    generator = RNGkind(),
    root_state = root_state,
    second_state = second_state,
    stream_one = stream_one,
    stream_two = stream_two,
    repeated_one = repeated_one,
    repeated_two = repeated_two
  )
}

stream_demo <- run_stream_demo()

stopifnot(
  !floating_exact_comparison,
  floating_toleranced_comparison,
  identical(dim(A), c(2L, 2L)),
  length(linear_solution) == 2L,
  is.finite(matrix_condition_number),
  matrix_condition_number >= 1,
  linear_residual_norm < 1e-12,
  identical(optimization$convergence, 0L),
  abs(unname(optimization$par) - 2) < 1e-7,
  abs(optimization$value - 1) < 1e-12,
  identical(stream_demo$generator[[1L]], "L'Ecuyer-CMRG"),
  identical(stream_demo$stream_one, stream_demo$repeated_one),
  identical(stream_demo$stream_two, stream_demo$repeated_two),
  !identical(stream_demo$stream_one, stream_demo$stream_two),
  !identical(stream_demo$root_state, stream_demo$second_state)
)

cat("0.1 + 0.2 tam eşit:", floating_exact_comparison, "\n")
cat("Pedagojik karma toleransla eşdeğer:",
    floating_toleranced_comparison, "\n")
cat("Doğrusal sistem artık normu:",
    format(linear_residual_norm, scientific = TRUE), "\n")
cat("Koşul sayısı:", sprintf("%.6f", matrix_condition_number), "\n")
cat("Optimizasyon çözümü:", sprintf("%.8f", optimization$par), "\n")
cat("Ayrı L'Ecuyer akışları yeniden üretildi: TRUE\n")

ch15_result <- TRUE
