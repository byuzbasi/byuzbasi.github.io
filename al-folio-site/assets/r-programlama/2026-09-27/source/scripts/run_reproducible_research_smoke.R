#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."),
                             mustWork = TRUE)

run_id <- Sys.getenv("REPRO_RESEARCH_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop(
    "REPRO_RESEARCH_RUN_ID zorunludur; örnek: v0.1-part3-smoke-01",
    call. = FALSE
  )
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("REPRO_RESEARCH_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
       call. = FALSE)
}

required_packages <- c(
  "jsonlite", "digest", "dplyr", "tidyr", "ggplot2", "knitr", "renv"
)
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

example_root <- file.path(project_dir, "companion", "v0.1", "examples")
example_paths <- c(
  ch13 = file.path(example_root, "ch13", "veriyi_donusturmek.R"),
  ch14 = file.path(example_root, "ch14", "grafiklerle_iletisim.R"),
  ch15 = file.path(example_root, "ch15", "sayisal_hesaplama_ve_rastgelelik.R"),
  ch16 = file.path(example_root, "ch16", "simulasyonu_dogru_kurmak.R"),
  ch17 = file.path(example_root, "ch17", "arastirma_projesinin_yasami.R")
)
report_template <- file.path(
  example_root, "ch17", "arastirma_raporu.Rmd"
)
prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
required_files <- c(example_paths, report_template, prototype_path)
if (any(!file.exists(required_files))) {
  stop("Kısım III örneklerinden, rapor şablonundan veya prototipten biri eksik.",
       call. = FALSE)
}

environment_names <- c(
  "RBOOK_PROJECT_DIR", "RBOOK_CH14_OUTPUT_DIR", "RBOOK_CH16_OUTPUT_DIR",
  "RBOOK_CH16_RUN_ID", "RBOOK_CH16_STOP_AFTER_CHUNKS",
  "RBOOK_CH16_SUMMARY_PATH", "RBOOK_CH17_OUTPUT_DIR"
)
old_environment <- stats::setNames(
  lapply(environment_names, function(name) {
    value <- Sys.getenv(name, unset = NA_character_)
    if (identical(value, NA_character_)) NA_character_ else value
  }),
  environment_names
)
restore_environment <- function() {
  for (name in names(old_environment)) {
    value <- old_environment[[name]]
    if (is.na(value)) {
      Sys.unsetenv(name)
    } else {
      do.call(Sys.setenv, stats::setNames(list(value), name))
    }
  }
}
on.exit(restore_environment(), add = TRUE)
Sys.setenv(RBOOK_PROJECT_DIR = project_dir)

source_example <- function(label, path, expected_result = NULL) {
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
  passed <- is.null(error_message)
  if (passed && !is.null(expected_result)) {
    passed <- exists(expected_result, envir = example_env, inherits = FALSE) &&
      isTRUE(get(expected_result, envir = example_env, inherits = FALSE))
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
  list(
    label = label,
    passed = passed,
    error = error_message,
    envir = example_env,
    output_path = output_path
  )
}

ch13_run <- source_example("ch13", example_paths[["ch13"]], "ch13_result")

ch14_output <- file.path(output_dir, "ch14-figures")
Sys.setenv(RBOOK_CH14_OUTPUT_DIR = ch14_output)
ch14_run <- source_example("ch14", example_paths[["ch14"]], "ch14_result")
Sys.unsetenv("RBOOK_CH14_OUTPUT_DIR")

ch15_run <- source_example("ch15", example_paths[["ch15"]], "ch15_result")

ch16_output <- file.path(output_dir, "ch16-main")
Sys.setenv(
  RBOOK_CH16_OUTPUT_DIR = ch16_output,
  RBOOK_CH16_RUN_ID = paste0(run_id, "-main"),
  RBOOK_CH16_STOP_AFTER_CHUNKS = "2"
)
ch16_partial <- source_example(
  "ch16_partial", example_paths[["ch16"]], "ch16_result"
)

Sys.setenv(RBOOK_CH16_STOP_AFTER_CHUNKS = "4")
ch16_resume <- source_example(
  "ch16_resume", example_paths[["ch16"]], "ch16_result"
)

corrupt_output <- file.path(output_dir, "ch16-corrupt-probe")
Sys.setenv(
  RBOOK_CH16_OUTPUT_DIR = corrupt_output,
  RBOOK_CH16_RUN_ID = paste0(run_id, "-corrupt-probe"),
  RBOOK_CH16_STOP_AFTER_CHUNKS = "1"
)
ch16_corrupt_initial <- source_example(
  "ch16_corrupt_initial", example_paths[["ch16"]], "ch16_result"
)
corrupt_path <- file.path(corrupt_output, "checkpoints", "chunk_001.rds")
if (!ch16_corrupt_initial$passed || !file.exists(corrupt_path)) {
  stop("Bozuk checkpoint sınaması için ilk geçerli parça üretilemedi.",
       call. = FALSE)
}
corrupted_shard <- readRDS(corrupt_path)
corrupted_shard$scientific_signature[[1L]] <- "deliberately-corrupted"
corrupt_temporary <- paste0(corrupt_path, ".corrupt")
saveRDS(corrupted_shard, corrupt_temporary, version = 3)
if (!file.rename(corrupt_temporary, corrupt_path)) {
  stop("Bozuk checkpoint deneme kopyası yerine taşınamadı.", call. = FALSE)
}
Sys.setenv(RBOOK_CH16_STOP_AFTER_CHUNKS = "2")
ch16_corrupt_resume <- source_example(
  "ch16_corrupt_resume", example_paths[["ch16"]], expected_result = NULL
)
corrupt_rejected <- !is.null(ch16_corrupt_resume$error) &&
  grepl("Geçersiz veya bilimsel imzası uyuşmayan checkpoint",
        ch16_corrupt_resume$error, fixed = TRUE)

if (!ch16_resume$passed ||
    !exists("ch16_pipeline", envir = ch16_resume$envir, inherits = FALSE) ||
    !isTRUE(ch16_resume$envir$ch16_pipeline$complete)) {
  stop("Bölüm 16 ana çalışma devam ettirilip tamamlanamadı.", call. = FALSE)
}
ch16_summary_path <- ch16_resume$envir$ch16_pipeline$summary_path

ch17_output <- file.path(output_dir, "ch17-report")
Sys.setenv(
  RBOOK_CH16_SUMMARY_PATH = ch16_summary_path,
  RBOOK_CH17_OUTPUT_DIR = ch17_output
)
ch17_run <- source_example("ch17", example_paths[["ch17"]], "ch17_result")

chapter_passed <- c(
  ch13 = ch13_run$passed &&
    inherits(ch13_run$envir$cardinality_error, "error"),
  ch14 = ch14_run$passed &&
    length(list.files(ch14_output, pattern = "\\.pdf$")) == 2L,
  ch15 = ch15_run$passed &&
    identical(ch15_run$envir$stream_demo$stream_one,
              ch15_run$envir$stream_demo$repeated_one),
  ch16 = ch16_partial$passed &&
    !isTRUE(ch16_partial$envir$ch16_pipeline$complete) &&
    identical(ch16_partial$envir$ch16_pipeline$completed, 32L) &&
    ch16_resume$passed &&
    isTRUE(ch16_resume$envir$ch16_pipeline$complete) &&
    identical(ch16_resume$envir$ch16_pipeline$completed, 64L) &&
    identical(ch16_resume$envir$ch16_pipeline$resumed_valid_work_units, 32L) &&
    corrupt_rejected,
  ch17 = ch17_run$passed && file.exists(ch17_run$envir$ch17_report_path)
)
chapter_notes <- c(
  ch13 = "base/tidy equivalence, pivot roundtrip, cardinality rejection",
  ch14 = "two vector PDFs; colour plus shape and linetype",
  ch15 = "floating point, linear solve, optimization, repeatable RNG streams",
  ch16 = "64 work units; 2+2 checkpoint resume; corrupt shard rejected",
  ch17 = "read-only input; kable report; no renv or Git mutation"
)
result_table <- data.frame(
  chapter = names(chapter_passed),
  passed = unname(chapter_passed),
  note = unname(chapter_notes[names(chapter_passed)]),
  stringsAsFactors = FALSE
)
result_tsv <- file.path(output_dir, "reproducible_research_smoke.tsv")
utils::write.table(
  result_table,
  result_tsv,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

environment_path <- file.path(output_dir, "environment.txt")
environment_lines <- c(
  paste0("run_id: ", run_id),
  paste0("R: ", R.version.string),
  paste0("platform: ", R.version$platform),
  paste0("locale: ", Sys.getlocale()),
  paste0("libPaths: ", paste(.libPaths(), collapse = " | ")),
  vapply(required_packages, function(package) {
    paste0(package, ": ", as.character(utils::packageVersion(package)))
  }, character(1)),
  "production_run: false",
  "renv_mutation_calls: none",
  "git_mutation_calls: none"
)
writeLines(environment_lines, environment_path, useBytes = TRUE)

all_passed <- all(result_table$passed)
result_json <- file.path(output_dir, "reproducible_research_smoke.json")
jsonlite::write_json(
  list(
    schema_version = "1.0",
    project_version = "v0.1",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    status = if (all_passed) "PASS" else "FAIL",
    scientific_contract = paste(
      "independent position-specific Bernoulli variables and the exact",
      "run-count reference distribution are unchanged"
    ),
    pedagogical_simulation = list(
      seed = 20260906L,
      rng = "L'Ecuyer-CMRG",
      work_unit = "one Monte Carlo replication",
      replications = 64L,
      checkpoint_layout = "4 checkpoints x 16 replications",
      production_recommendation = FALSE,
      pass_based_on_closeness_to_exact_probability = FALSE
    ),
    checkpoint_resume = list(
      first_pass_validated = 32L,
      resumed_to = 64L,
      corrupt_checkpoint_rejected = corrupt_rejected
    ),
    results = result_table
  ),
  result_json,
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}
generated_paths <- list.files(
  output_dir,
  recursive = TRUE,
  full.names = TRUE,
  all.files = FALSE
)
generated_paths <- generated_paths[file.info(generated_paths)$isdir %in% FALSE]
manifest_paths <- sort(unique(c(
  prototype_path,
  example_paths,
  report_template,
  script_path,
  generated_paths
)))
manifest_entries <- lapply(manifest_paths, function(path) {
  list(
    path = relative_path(path),
    bytes = unname(file.info(path)$size),
    sha256 = digest::digest(file = path, algo = "sha256", serialize = FALSE)
  )
})
manifest_path <- file.path(output_dir, "manifest.json")
jsonlite::write_json(
  list(
    schema_version = "1.0",
    project_version = "v0.1",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    scientific_signature = ch16_resume$envir$scientific_signature,
    files = manifest_entries
  ),
  manifest_path,
  pretty = TRUE,
  auto_unbox = TRUE
)

print(result_table, row.names = FALSE)
cat("Bölüm 16 geçerli iş birimi: 64/64\n")
cat("Bozuk checkpoint reddedildi:", corrupt_rejected, "\n")
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
