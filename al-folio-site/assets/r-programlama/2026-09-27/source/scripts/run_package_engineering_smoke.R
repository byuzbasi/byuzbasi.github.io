#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."),
                             mustWork = TRUE)

run_id <- Sys.getenv("PACKAGE_ENGINEERING_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop(
    "PACKAGE_ENGINEERING_RUN_ID zorunludur; örnek: v0.1-part4-smoke-01",
    call. = FALSE
  )
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop(
    "PACKAGE_ENGINEERING_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
    call. = FALSE
  )
}

required_packages <- c("jsonlite", "digest", "testthat", "roxygen2", "knitr")
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
  stop(
    "Duman sınaması kimliği zaten var; üzerine yazılmadı: ", run_id,
    call. = FALSE
  )
}
dir.create(file.path(output_dir, "outputs"), recursive = TRUE,
           showWarnings = FALSE)

example_root <- file.path(project_dir, "companion", "v0.1", "examples")
example_paths <- c(
  ch18 = file.path(example_root, "ch18", "guvenilir_api.R"),
  ch20 = file.path(example_root, "ch20", "metadata_ve_ad_alani.R"),
  ch21 = file.path(example_root, "ch21", "belgeleme_ve_ornekler.R"),
  ch22 = file.path(example_root, "ch22", "test_tasarimi.R"),
  ch23 = file.path(example_root, "ch23", "uzun_belgeleri_uretmek.R"),
  ch24 = file.path(example_root, "ch24", "paket_denetime_hazirlik.R")
)
chapter_23_template <- file.path(
  example_root, "ch23", "paket_rehberi.Rmd"
)
prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
required_files <- c(example_paths, chapter_23_template, prototype_path)
if (any(!file.exists(required_files))) {
  stop("Kısım IV örneği, uzun belge kaynağı veya prototip eksik.",
       call. = FALSE)
}

prototype_hash_before <- digest::digest(
  file = prototype_path, algo = "sha256", serialize = FALSE
)

environment_names <- c("RBOOK_PROJECT_DIR", "RBOOK_CH23_OUTPUT_DIR")
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
Sys.setenv(
  RBOOK_PROJECT_DIR = project_dir,
  RBOOK_CH23_OUTPUT_DIR = file.path(output_dir, "ch23-guide")
)

source_example <- function(label, path, expected_result) {
  example_environment <- new.env(parent = baseenv())
  error_message <- NULL
  visible_output <- tryCatch(
    utils::capture.output(
      sys.source(path, envir = example_environment, keep.source = TRUE)
    ),
    error = function(cnd) {
      error_message <<- conditionMessage(cnd)
      character()
    }
  )
  passed <- is.null(error_message) &&
    exists(expected_result, envir = example_environment, inherits = FALSE) &&
    isTRUE(get(expected_result, envir = example_environment, inherits = FALSE))
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
    envir = example_environment,
    output_path = output_path
  )
}

runs <- lapply(names(example_paths), function(label) {
  source_example(
    label,
    example_paths[[label]],
    paste0(label, "_result")
  )
})
names(runs) <- names(example_paths)

prototype_hash_after <- digest::digest(
  file = prototype_path, algo = "sha256", serialize = FALSE
)
prototype_unchanged <- identical(prototype_hash_before, prototype_hash_after)

# Bu tarihsel öğretim sınaması üst dizinlerde metadata üretmemelidir. Gerçek
# BernoulliRuns paket adayı kendi alt dizininde bulunabilir; bu betik onu
# oluşturmaz, değiştirmez, build etmez veya kurmaz.
forbidden_package_files <- file.path(
  project_dir,
  c(
    "DESCRIPTION", "NAMESPACE",
    "companion/v0.1/capstone-package/DESCRIPTION",
    "companion/v0.1/capstone-package/NAMESPACE"
  )
)
no_persistent_package_metadata <- all(!file.exists(forbidden_package_files))
candidate_package_dir <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "BernoulliRuns"
)
candidate_package_tree_present <- all(file.exists(file.path(
  candidate_package_dir, c("DESCRIPTION", "NAMESPACE")
)))

chapter_passed <- vapply(runs, function(run) run$passed, logical(1))
chapter_notes <- c(
  ch18 = "API responsibilities, classed errors, input and process state",
  ch20 = "in-memory DCF and read-only installed namespace inspection",
  ch21 = "roxygen processing, temporary Rd parse, runnable example",
  ch22 = "exhaustive n=1..8 enumeration and contract invariants",
  ch23 = "offline knitr guide with kable role tables",
  ch24 = "R CMD help probes and synthetic diagnostic classification"
)
result_table <- data.frame(
  chapter = names(chapter_passed),
  passed = unname(chapter_passed),
  note = unname(chapter_notes[names(chapter_passed)]),
  stringsAsFactors = FALSE
)
utils::write.table(
  result_table,
  file.path(output_dir, "package_engineering_smoke.tsv"),
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
  paste0("prototype_sha256_before: ", prototype_hash_before),
  paste0("prototype_sha256_after: ", prototype_hash_after),
  "production_run: false",
  "package_build_or_check_run: false",
  "persistent_DESCRIPTION_or_NAMESPACE_created_by_smoke: false",
  paste0("candidate_package_tree_present: ", candidate_package_tree_present),
  "package_install_or_update: none",
  "git_or_remote_mutation: none"
)
writeLines(environment_lines, environment_path, useBytes = TRUE)

all_passed <- all(result_table$passed) &&
  prototype_unchanged &&
  no_persistent_package_metadata
result_json <- file.path(output_dir, "package_engineering_smoke.json")
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
    scope = list(
      production_run = FALSE,
      package_tree_created_by_this_smoke = FALSE,
      candidate_package_tree_present = candidate_package_tree_present,
      # Geriye dönük şema alanı: yalnız bu smoke çalışmasının eylemini anlatır.
      actual_package_tree_created = FALSE,
      package_build_or_check_run = FALSE,
      package_install_or_update = "none",
      remote_or_git_mutation = "none"
    ),
    prototype = list(
      sha256_before = prototype_hash_before,
      sha256_after = prototype_hash_after,
      unchanged = prototype_unchanged
    ),
    persistent_package_metadata_absent = no_persistent_package_metadata,
    persistent_package_metadata_created_by_smoke = FALSE,
    exhaustive_validation = list(
      maximum_n = 8L,
      total_binary_sequences = sum(2^(seq_len(8L))),
      tolerance = 1e-12,
      tolerance_scope = "small deterministic smoke validation only"
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
  chapter_23_template,
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
jsonlite::write_json(
  list(
    schema_version = "1.0",
    project_version = "v0.1",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    scientific_signature = paste(
      "exact total run-count distribution; independent non-identically",
      "distributed Bernoulli sequence; package-neutral reference unchanged"
    ),
    files = manifest_entries
  ),
  file.path(output_dir, "manifest.json"),
  pretty = TRUE,
  auto_unbox = TRUE
)

print(result_table, row.names = FALSE)
cat("Saf-R prototip değişmedi:", prototype_unchanged, "\n")
cat("Öğretim sınaması üst dizinlerde paket metadata'sı oluşturmadı:",
    no_persistent_package_metadata, "\n")
cat("BernoulliRuns paket adayı mevcut:", candidate_package_tree_present, "\n")
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
