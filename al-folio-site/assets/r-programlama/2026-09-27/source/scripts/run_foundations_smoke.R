#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

run_id <- Sys.getenv("FOUNDATIONS_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop("FOUNDATIONS_RUN_ID zorunludur; örnek: v0.1-foundations-01", call. = FALSE)
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("FOUNDATIONS_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
       call. = FALSE)
}

required_packages <- c("jsonlite", "digest")
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
  ch02 = file.path(example_root, "ch02", "nesneler_ve_vektorler.R"),
  ch03 = file.path(example_root, "ch03", "indeksleme_ve_vektorlestirme.R"),
  ch04 = file.path(example_root, "ch04", "bilesik_veri_yapilari.R"),
  ch05 = file.path(example_root, "ch05", "dosyalari_guvenle_okumak.R")
)
if (any(!file.exists(example_paths))) {
  stop("Başlangıç bölümü örneklerinden en az biri eksik.", call. = FALSE)
}

run_example <- function(label, path) {
  example_env <- new.env(parent = baseenv())
  error_message <- NULL
  visible_output <- tryCatch(
    utils::capture.output(
      sys.source(path, envir = example_env, keep.source = TRUE)
    ),
    error = function(e) {
      error_message <<- conditionMessage(e)
      character()
    }
  )

  result_name <- paste0(label, "_result")
  passed <- is.null(error_message) &&
    exists(result_name, envir = example_env, inherits = FALSE)
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
    output_path = output_path
  )
}

old_script_dir <- Sys.getenv("RBOOK_CH05_SCRIPT_DIR", unset = NA_character_)
old_output_dir <- Sys.getenv("RBOOK_CH05_OUTPUT_DIR", unset = NA_character_)
restore_environment <- function(name, value) {
  if (is.na(value)) {
    Sys.unsetenv(name)
  } else {
    do.call(Sys.setenv, stats::setNames(list(value), name))
  }
}
on.exit(restore_environment("RBOOK_CH05_SCRIPT_DIR", old_script_dir), add = TRUE)
on.exit(restore_environment("RBOOK_CH05_OUTPUT_DIR", old_output_dir), add = TRUE)

Sys.setenv(
  RBOOK_CH05_SCRIPT_DIR = dirname(example_paths[["ch05"]]),
  RBOOK_CH05_OUTPUT_DIR = file.path(output_dir, "ch05-output")
)

run_results <- lapply(names(example_paths), function(label) {
  run_example(label, example_paths[[label]])
})

result_table <- data.frame(
  chapter = vapply(run_results, `[[`, character(1), "label"),
  passed = vapply(run_results, `[[`, logical(1), "passed"),
  error = vapply(run_results, function(x) {
    if (is.null(x$error)) "" else x$error
  }, character(1)),
  stringsAsFactors = FALSE
)
utils::write.table(
  result_table,
  file.path(output_dir, "foundations_smoke.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

environment_lines <- c(
  paste0("run_id: ", run_id),
  paste0("R: ", R.version.string),
  paste0("platform: ", R.version$platform),
  paste0("locale: ", Sys.getlocale()),
  paste0("native_encoding: ", l10n_info()[["codepage"]]),
  paste0("libPaths: ", paste(.libPaths(), collapse = " | ")),
  paste0("jsonlite: ", as.character(utils::packageVersion("jsonlite"))),
  paste0("digest: ", as.character(utils::packageVersion("digest")))
)
writeLines(environment_lines, file.path(output_dir, "environment.txt"),
           useBytes = TRUE)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}

data_paths <- c(
  file.path(example_root, "ch05", "data", "ogrenciler_utf8.csv"),
  file.path(example_root, "ch05", "data", "VERI_NOTU.md")
)
result_paths <- c(
  file.path(output_dir, "foundations_smoke.tsv"),
  file.path(output_dir, "environment.txt"),
  vapply(run_results, `[[`, character(1), "output_path"),
  file.path(output_dir, "ch05-output", "grup_ozeti.csv")
)
manifest_paths <- c(example_paths, data_paths, result_paths)
manifest_paths <- manifest_paths[file.exists(manifest_paths)]
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
    work_unit = "one deterministic executable example per chapter",
    total_work_units = nrow(result_table),
    results = result_table,
    files = manifest_entries
  ),
  file.path(output_dir, "foundations_smoke.json"),
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

print(result_table, row.names = FALSE)
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
