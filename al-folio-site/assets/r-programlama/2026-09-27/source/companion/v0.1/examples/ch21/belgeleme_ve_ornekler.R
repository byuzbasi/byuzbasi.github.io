# Bölüm 21: roxygen2 girdisini bellek/geçici dosya üzerinden doğrulamak.

project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  stop("RBOOK_PROJECT_DIR zorunludur.", call. = FALSE)
}
project_dir <- normalizePath(project_dir, mustWork = TRUE)

if (!requireNamespace("roxygen2", quietly = TRUE)) {
  stop("Kurulu roxygen2 paketi gereklidir; otomatik kurulum yapılmadı.",
       call. = FALSE)
}

prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
prototype_environment <- new.env(parent = baseenv())
sys.source(prototype_path, envir = prototype_environment, keep.source = TRUE)
runs_distribution_reference <- get(
  "runs_distribution_reference", envir = prototype_environment,
  inherits = FALSE
)

teaching_runs_distribution <- function(prob) {
  runs_distribution_reference(prob)
}

function_roxygen <- c(
  "#' Exact run-count distribution",
  "#'",
  "#' Computes a teaching view of the exact distribution under independent",
  "#' Bernoulli trials with position-specific probabilities.",
  "#'",
  "#' @param prob A finite numeric vector with values in the closed interval",
  "#'   from zero to one.",
  "#' @return A data frame with run counts, probabilities, and cumulative",
  "#'   probabilities.",
  "#' @examples",
  "#' teaching_runs_distribution(c(0.2, 0.5, 0.8))",
  "teaching_runs_distribution <- function(prob) NULL"
)

data_roxygen <- c(
  "#' Synthetic probability vector",
  "#'",
  "#' A three-element numeric vector used only in documentation examples.",
  "#'",
  "#' @format A numeric vector of length three.",
  "#' @source Constructed for this book; no external data source.",
  "example_probabilities <- c(0.2, 0.5, 0.8)"
)

function_topics <- roxygen2::roc_proc_text(
  roxygen2::rd_roclet(), function_roxygen
)
data_topics <- roxygen2::roc_proc_text(
  roxygen2::rd_roclet(), data_roxygen
)
if (length(function_topics) != 1L || length(data_topics) != 1L) {
  stop("Beklenen roxygen konu sayısı üretilemedi.", call. = FALSE)
}

function_rd <- function_topics[[1L]]$format()
data_rd <- data_topics[[1L]]$format()

function_rd_path <- tempfile("ch21-function-", fileext = ".Rd")
data_rd_path <- tempfile("ch21-data-", fileext = ".Rd")
on.exit(unlink(c(function_rd_path, data_rd_path), force = TRUE), add = TRUE)
writeLines(function_rd, function_rd_path, useBytes = TRUE)
writeLines(data_rd, data_rd_path, useBytes = TRUE)

parsed_function_rd <- tools::parse_Rd(
  function_rd_path, encoding = "UTF-8", fragment = FALSE
)
parsed_data_rd <- tools::parse_Rd(
  data_rd_path, encoding = "UTF-8", fragment = FALSE
)

example_value <- teaching_runs_distribution(c(0.2, 0.5, 0.8))
documentation_contract <- data.frame(
  component = c("arguments", "return value", "errors", "examples", "data"),
  required_question = c(
    "What values and shapes are accepted?",
    "What class, names, and meaning are returned?",
    "Which invalid inputs raise which condition?",
    "Can the code run quickly in a clean session?",
    "What is the source, structure, unit, and license?"
  ),
  stringsAsFactors = FALSE
)

ch21_result <- inherits(parsed_function_rd, "Rd") &&
  inherits(parsed_data_rd, "Rd") &&
  grepl("\\\\arguments\\{", function_rd) &&
  grepl("\\\\value\\{", function_rd) &&
  grepl("\\\\examples\\{", function_rd) &&
  grepl("\\\\format\\{", data_rd) &&
  grepl("\\\\source\\{", data_rd) &&
  identical(names(example_value), c("runs", "probability", "cumulative")) &&
  isTRUE(all.equal(sum(example_value$probability), 1, tolerance = 1e-12)) &&
  nrow(documentation_contract) == 5L

if (!isTRUE(ch21_result)) {
  stop("Bölüm 21 belge ve örnek denetimi başarısız.", call. = FALSE)
}

cat("Bölüm 21: roxygen metni, Rd ayrıştırma ve çalışır örnek geçti.\n")
