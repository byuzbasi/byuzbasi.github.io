args_full <- commandArgs(trailingOnly = FALSE)
project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) stop("Betik yolu belirlenemedi.", call. = FALSE)
  script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
  project_dir <- normalizePath(
    file.path(dirname(script_path), "..", "..", "..", ".."),
    mustWork = TRUE
  )
}

source(
  file.path(project_dir, "companion", "v0.1", "capstone-package",
            "prototype", "bernoulli_runs_reference.R"),
  local = TRUE,
  encoding = "UTF-8"
)

validate_prob_scenarios <- function(prob_list) {
  if (!is.list(prob_list) || length(prob_list) == 0L) {
    abort_runs_input("`prob_list` boş olmayan bir liste olmalıdır.",
                     "prob_list")
  }
  scenario_names <- names(prob_list)
  if (is.null(scenario_names) || any(!nzchar(scenario_names)) ||
      anyDuplicated(scenario_names)) {
    abort_runs_input(
      "`prob_list` benzersiz ve boş olmayan senaryo adları taşımalıdır.",
      "prob_list"
    )
  }
  validated <- lapply(prob_list, validate_run_probabilities)
  names(validated) <- scenario_names
  validated
}

runs_batch_loop <- function(prob_list) {
  prob_list <- validate_prob_scenarios(prob_list)
  result <- vector("list", length(prob_list))
  names(result) <- names(prob_list)
  for (i in seq_along(prob_list)) {
    result[[i]] <- runs_distribution_reference(prob_list[[i]])
  }
  result
}

runs_batch_lapply <- function(prob_list) {
  prob_list <- validate_prob_scenarios(prob_list)
  lapply(prob_list, runs_distribution_reference)
}

summarize_runs_batch <- function(batch) {
  if (!is.list(batch) || length(batch) == 0L || is.null(names(batch))) {
    abort_runs_input("`batch` adlı ve boş olmayan bir liste olmalıdır.",
                     "batch")
  }
  data.frame(
    scenario = names(batch),
    n = vapply(batch, nrow, integer(1)),
    expected_runs = vapply(
      batch,
      function(tbl) sum(tbl$runs * tbl$probability),
      numeric(1)
    ),
    stringsAsFactors = FALSE,
    row.names = NULL
  )
}

runs_tail_batch <- function(x_list, prob_list, tail = c("lower", "upper")) {
  tail <- match.arg(tail)
  if (!is.list(x_list) || length(x_list) == 0L) {
    abort_runs_input("`x_list` boş olmayan bir liste olmalıdır.", "x_list")
  }
  prob_list <- validate_prob_scenarios(prob_list)
  if (length(x_list) != length(prob_list)) {
    abort_runs_input(
      "`x_list` ile `prob_list` aynı sayıda senaryo taşımalıdır.",
      "x_list"
    )
  }
  if (!is.null(names(x_list)) && !identical(names(x_list), names(prob_list))) {
    abort_runs_input(
      "Adlandırılmış `x_list` ile `prob_list` aynı ad ve sırayı taşımalıdır.",
      "x_list"
    )
  }
  names(x_list) <- names(prob_list)
  Map(
    function(x, prob) runs_tail_reference(x, prob, tail = tail),
    x_list,
    prob_list
  )
}

prob_scenarios <- list(
  alternating = c(0.15, 0.85, 0.20, 0.80),
  balanced = rep(0.50, 4L),
  early_shift = c(0.10, 0.20, 0.80, 0.90, 0.70)
)
prob_snapshot <- prob_scenarios

batch_loop <- runs_batch_loop(prob_scenarios)
batch_lapply <- runs_batch_lapply(prob_scenarios)
batch_summary <- summarize_runs_batch(batch_lapply)

fold_cumulative <- Reduce(
  `+`,
  batch_lapply$alternating$probability,
  accumulate = TRUE
)

observed <- list(
  alternating = c(0L, 1L, 0L, 1L),
  balanced = c(0L, 0L, 1L, 1L),
  early_shift = c(0L, 0L, 1L, 1L, 1L)
)
tail_results <- runs_tail_batch(observed, prob_scenarios, tail = "upper")
tail_probabilities <- vapply(tail_results, `[[`, numeric(1), "p.value")

stable_shape <- sapply(list(a = 1, b = 2), identity)
unstable_shape <- sapply(list(a = 1, b = 1:2), identity)
vapply_shape_error <- tryCatch(
  vapply(list(a = 1, b = 1:2), identity, numeric(1)),
  error = function(cnd) cnd
)
recycling_error <- tryCatch(
  runs_tail_batch(observed[-1L], prob_scenarios, tail = "upper"),
  runs_input_error = function(cnd) cnd
)

stopifnot(
  identical(batch_loop, batch_lapply),
  identical(prob_scenarios, prob_snapshot),
  identical(names(batch_summary), c("scenario", "n", "expected_runs")),
  identical(batch_summary$n, c(4L, 4L, 5L)),
  all(is.finite(batch_summary$expected_runs)),
  max(abs(fold_cumulative -
            batch_lapply$alternating$cumulative)) < 1e-12,
  length(tail_probabilities) == length(prob_scenarios),
  all(tail_probabilities >= 0 & tail_probabilities <= 1),
  is.numeric(stable_shape),
  is.list(unstable_shape),
  inherits(vapply_shape_error, "error"),
  inherits(recycling_error, "runs_input_error"),
  identical(recycling_error$argument, "x_list")
)

cat("Senaryo sayısı:", length(prob_scenarios), "\n")
cat("Döngü ve lapply eşdeğer:", identical(batch_loop, batch_lapply), "\n")
cat("Özet sütunları:", paste(names(batch_summary), collapse = ", "), "\n")
cat("Üst kuyruklar:",
    paste(sprintf("%.6f", tail_probabilities), collapse = ", "), "\n")
cat("Girdi değişmedi:", identical(prob_scenarios, prob_snapshot), "\n")

ch11_result <- TRUE
