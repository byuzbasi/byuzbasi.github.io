args_full <- commandArgs(trailingOnly = FALSE)
project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) stop("Betik yolu belirlenemedi.", call. = FALSE)
  script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
  project_dir <- normalizePath(file.path(dirname(script_path), "..", "..", "..", ".."), mustWork = TRUE)
}

source(
  file.path(project_dir, "companion", "v0.1", "capstone-package",
            "prototype", "bernoulli_runs_reference.R"),
  local = TRUE,
  encoding = "UTF-8"
)

runs_table <- function(prob, cumulative = TRUE) {
  if (!is.logical(cumulative) || length(cumulative) != 1L ||
      is.na(cumulative)) {
    abort_runs_input("`cumulative` tek ve eksiksiz mantıksal değer olmalıdır.",
                     "cumulative")
  }
  result <- runs_distribution_reference(prob)
  if (!cumulative) result$cumulative <- NULL
  result
}

format_probability <- function(x, ...) {
  formatC(x, format = "f", ...)
}

print_runs_table <- function(x, digits = 5L) {
  printable <- x
  printable$probability <- format_probability(
    printable$probability,
    digits = digits
  )
  if ("cumulative" %in% names(printable)) {
    printable$cumulative <- format_probability(
      printable$cumulative,
      digits = digits
    )
  }
  print(printable, row.names = FALSE)
  invisible(x)
}

prob <- c(0.20, 0.45, 0.70, 0.60)
dagilim <- runs_table(prob)
geri_donen <- print_runs_table(dagilim, digits = 5L)

stopifnot(
  identical(names(dagilim), c("runs", "probability", "cumulative")),
  identical(geri_donen, dagilim),
  nrow(dagilim) == length(prob),
  abs(utils::tail(dagilim$cumulative, 1L) - 1) < 1e-12
)

cat("Satır sayısı:", nrow(dagilim), "\n")
cat("Görünmez dönüş korunuyor:", identical(geri_donen, dagilim), "\n")

ch07_result <- TRUE
