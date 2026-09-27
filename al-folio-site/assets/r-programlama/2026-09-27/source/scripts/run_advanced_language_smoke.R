#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."),
                             mustWork = TRUE)

run_id <- Sys.getenv("ADVANCED_LANGUAGE_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop(
    "ADVANCED_LANGUAGE_RUN_ID zorunludur; örnek: v0.1-advanced-language-01",
    call. = FALSE
  )
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop(
    "ADVANCED_LANGUAGE_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
    call. = FALSE
  )
}

required_packages <- c("jsonlite", "digest", "R6", "rlang")
missing_packages <- required_packages[!vapply(
  required_packages,
  requireNamespace,
  quietly = TRUE,
  FUN.VALUE = logical(1)
)]
if (length(missing_packages)) {
  stop(
    "Eksik paketler: ", paste(missing_packages, collapse = ", "),
    ". Otomatik kurulum yapılmadı.",
    call. = FALSE
  )
}

output_dir <- file.path(project_dir, "validation", "v0.1", run_id)
if (file.exists(output_dir)) {
  stop("Duman sınaması kimliği zaten var; üzerine yazılmadı: ", run_id,
       call. = FALSE)
}
dir.create(file.path(output_dir, "outputs"), recursive = TRUE,
           showWarnings = FALSE)

prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
example_root <- file.path(project_dir, "companion", "v0.1", "examples")
example_paths <- c(
  ch11 = file.path(example_root, "ch11", "yineleme_ve_islevseller.R"),
  ch12 = file.path(
    example_root, "ch12", "nesne_sistemleri_ve_ustprogramlama.R"
  )
)
required_files <- c(prototype_path, example_paths)
if (any(!file.exists(required_files))) {
  stop("İleri dil örneklerinden veya saf-R prototipinden en az biri eksik.",
       call. = FALSE)
}

run_example <- function(label, path) {
  example_env <- new.env(parent = baseenv())
  error_message <- NULL
  visible_output <- tryCatch(
    utils::capture.output(
      sys.source(path, envir = example_env, keep.source = TRUE)
    ),
    error = function(cnd) {
      error_message <<- conditionMessage(cnd)
      character()
    }
  )

  result_name <- paste0(label, "_result")
  passed <- is.null(error_message) &&
    exists(result_name, envir = example_env, inherits = FALSE) &&
    isTRUE(get(result_name, envir = example_env, inherits = FALSE))

  if (passed && identical(label, "ch11")) {
    passed <- isTRUE(
      identical(example_env$batch_loop, example_env$batch_lapply) &&
        identical(example_env$prob_scenarios, example_env$prob_snapshot) &&
        inherits(example_env$recycling_error, "runs_input_error") &&
        inherits(example_env$vapply_shape_error, "error")
    )
  }
  if (passed && identical(label, "ch12")) {
    passed <- isTRUE(
      inherits(example_env$s3_distribution, "runs_distribution_demo") &&
        abs(example_env$s4_total - 1) < 1e-12 &&
        inherits(example_env$s4_invalid, "error") &&
        identical(example_env$original_status$batches, 1L) &&
        identical(example_env$clone_status$batches, 2L) &&
        abs(example_env$tidy_mask_mean - example_env$base_mask_mean) < 1e-12
    )
  }

  output_path <- file.path(output_dir, "outputs", paste0(label, ".txt"))
  writeLines(
    c(
      paste0("status: ", if (passed) "PASS" else "FAIL"),
      if (!is.null(error_message)) paste0("error: ", error_message),
      visible_output
    ),
    output_path,
    useBytes = TRUE
  )
  list(label = label, passed = passed, error = error_message,
       output_path = output_path)
}

old_project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = NA_character_)
on.exit({
  if (is.na(old_project_dir)) {
    Sys.unsetenv("RBOOK_PROJECT_DIR")
  } else {
    Sys.setenv(RBOOK_PROJECT_DIR = old_project_dir)
  }
}, add = TRUE)
Sys.setenv(RBOOK_PROJECT_DIR = project_dir)

run_results <- lapply(names(example_paths), function(label) {
  run_example(label, example_paths[[label]])
})

result_table <- data.frame(
  work_unit = vapply(run_results, `[[`, character(1), "label"),
  passed = vapply(run_results, `[[`, logical(1), "passed"),
  error = vapply(run_results, function(x) {
    if (is.null(x$error)) "" else x$error
  }, character(1)),
  stringsAsFactors = FALSE
)
utils::write.table(
  result_table,
  file.path(output_dir, "advanced_language_smoke.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

environment_lines <- c(
  paste0("run_id: ", run_id),
  paste0("R: ", R.version.string),
  paste0("platform: ", R.version$platform),
  paste0("locale: ", Sys.getlocale()),
  paste0("libPaths: ", paste(.libPaths(), collapse = " | ")),
  vapply(required_packages, function(package) {
    paste0(package, ": ", as.character(utils::packageVersion(package)))
  }, character(1))
)
writeLines(environment_lines, file.path(output_dir, "environment.txt"),
           useBytes = TRUE)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}

result_paths <- c(
  file.path(output_dir, "advanced_language_smoke.tsv"),
  file.path(output_dir, "environment.txt"),
  vapply(run_results, `[[`, character(1), "output_path")
)
manifest_paths <- c(prototype_path, example_paths, script_path, result_paths)
manifest_entries <- lapply(manifest_paths, function(path) {
  list(
    path = relative_path(path),
    bytes = unname(file.info(path)$size),
    sha256 = digest::digest(file = path, algo = "sha256", serialize = FALSE)
  )
})

all_passed <- all(result_table$passed)
jsonlite::write_json(
  list(
    schema_version = "1.0",
    project_version = "v0.1",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    status = if (all_passed) "PASS" else "FAIL",
    scientific_contract = paste(
      "the exact run-count reference distribution is reused without",
      "changing its model, estimand, inputs, or numerical method"
    ),
    pedagogical_scope = paste(
      "iteration output contracts plus isolated S3, S4, R6, and",
      "data-mask demonstrations"
    ),
    work_unit = "one separately sourced example per chapter",
    total_work_units = nrow(result_table),
    results = result_table,
    files = manifest_entries
  ),
  file.path(output_dir, "advanced_language_smoke.json"),
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

print(result_table, row.names = FALSE)
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
