#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

run_id <- Sys.getenv("RELEASE_READINESS_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop("RELEASE_READINESS_RUN_ID zorunludur; örnek: v0.1-part6-smoke-01",
       call. = FALSE)
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("RELEASE_READINESS_RUN_ID yalnız güvenli ASCII karakterleri içerebilir.",
       call. = FALSE)
}
if (!requireNamespace("jsonlite", quietly = TRUE) ||
    !requireNamespace("digest", quietly = TRUE)) {
  stop("Kurulu jsonlite ve digest paketleri gereklidir; otomatik kurulum yapılmadı.",
       call. = FALSE)
}

output_dir <- file.path(project_dir, "validation", "v0.1", run_id)
if (file.exists(output_dir)) {
  stop("Çalışma kimliği zaten var; üzerine yazılmadı: ", run_id,
       call. = FALSE)
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}

write_json_atomic <- function(object, path) {
  temporary <- paste0(path, ".tmp")
  jsonlite::write_json(
    object,
    temporary,
    auto_unbox = TRUE,
    pretty = TRUE,
    null = "null",
    digits = NA
  )
  if (!file.rename(temporary, path)) {
    stop("JSON çıktısı atomik olarak taşınamadı: ", path, call. = FALSE)
  }
}

example_paths <- file.path(
  project_dir,
  "companion",
  "v0.1",
  "examples",
  c(
    "ch30/yayin_adayi_kapisi.R",
    "ch31/cran_geri_bildirim.R",
    "ch32/bakim_matrisi.R"
  )
)
if (any(!file.exists(example_paths))) {
  stop("Bölüm 30-32 örneklerinden en az biri bulunamadı.", call. = FALSE)
}

example_envs <- lapply(example_paths, function(path) {
  env <- new.env(parent = baseenv())
  sys.source(path, envir = env, keep.source = TRUE)
  env
})
names(example_envs) <- c("ch30", "ch31", "ch32")

results <- list()
add_result <- function(name, passed, observed, expected) {
  results[[length(results) + 1L]] <<- list(
    name = name,
    passed = isTRUE(passed),
    observed = observed,
    expected = expected
  )
}

prototype_path <- file.path(
  project_dir,
  "companion",
  "v0.1",
  "capstone-package",
  "prototype",
  "bernoulli_runs_reference.R"
)
prototype_expected <-
  "ad2098c4b80cd72625ae894f547a76c1b7ab535e5089a3a68dfb3589ab36912c"
prototype_before <- digest::digest(
  file = prototype_path,
  algo = "sha256",
  serialize = FALSE
)

snapshot <- example_envs$ch30$sglasso_case_snapshot()
sglasso_audit <- example_envs$ch30$audit_package_name(
  snapshot$github_research_package$package,
  current_cran = snapshot$existing_cran_package$package
)
mixed_case_audit <- example_envs$ch30$audit_package_name(
  "SgLaSsO",
  current_cran = "sglasso"
)
clear_audit <- example_envs$ch30$audit_package_name(
  "teachingRuns",
  current_cran = c("sglasso", "stats"),
  past_cran = "oldExample",
  current_bioconductor = "BioExample"
)
add_result(
  "sglasso_name_conflict_detected",
  !sglasso_audit$clear &&
    sglasso_audit$checks$conflict[sglasso_audit$checks$registry == "current_cran"],
  sglasso_audit$clear,
  FALSE
)
add_result(
  "case_insensitive_name_audit",
  !mixed_case_audit$clear,
  mixed_case_audit$normalized,
  "sglasso conflict"
)
add_result(
  "synthetic_clear_name",
  clear_audit$clear,
  clear_audit$clear,
  TRUE
)

blocked_gate <- example_envs$ch30$release_gate(list(
  identity_approved = TRUE,
  license_approved = TRUE,
  name_clear = FALSE,
  tests_passed = TRUE,
  source_archive_hashed = TRUE,
  r_release_check_passed = TRUE,
  r_devel_check_passed = TRUE,
  documentation_built = TRUE,
  secrets_absent = TRUE
))
passing_gate <- example_envs$ch30$release_gate(list(
  identity_approved = TRUE,
  license_approved = TRUE,
  name_clear = TRUE,
  tests_passed = TRUE,
  source_archive_hashed = TRUE,
  r_release_check_passed = TRUE,
  r_devel_check_passed = TRUE,
  documentation_built = TRUE,
  secrets_absent = TRUE
))
add_result(
  "release_gate_blocks_name_conflict",
  !blocked_gate$passed,
  blocked_gate$passed,
  FALSE
)
add_result(
  "complete_synthetic_release_gate",
  passing_gate$passed,
  passing_gate$passed,
  TRUE
)

diagnostics <- example_envs$ch31$classify_cran_diagnostics(c(
  "* checking R files for syntax errors ... ERROR",
  "* checking whether package can be installed ... WARNING",
  "* checking CRAN incoming feasibility ... NOTE",
  "Status: 1 ERROR, 1 WARNING, 1 NOTE"
))
responses <- data.frame(
  diagnostic_id = diagnostics$diagnostic_id,
  disposition = c("fixed", "fixed", "explained"),
  action = c(
    "Syntax error corrected.",
    "Missing declaration added.",
    "New submission note documented."
  ),
  evidence = c(
    "R parser passes.",
    "Clean installation passes.",
    "cran-comments.md contains the explanation."
  ),
  stringsAsFactors = FALSE
)
response_audit <- example_envs$ch31$evaluate_cran_responses(
  diagnostics,
  responses
)
sequence_audit <- example_envs$ch31$validate_submission_sequence(
  c(
    "source_frozen",
    "tarball_built",
    "tarball_checked",
    "form_submitted",
    "email_confirmed",
    "feedback_received",
    "response_prepared",
    "version_increased",
    "resubmitted"
  ),
  resubmission = TRUE
)
comments <- example_envs$ch31$render_cran_comments(
  "teachingPackage",
  "0.1.0",
  data.frame(
    platform = c("local-macos", "r-devel-linux"),
    r_version = c("release", "devel"),
    status = c("OK", "NOTE"),
    stringsAsFactors = FALSE
  ),
  "The remaining NOTE is explained with local evidence."
)
add_result(
  "diagnostics_classified",
  identical(diagnostics$severity, c("ERROR", "WARNING", "NOTE")),
  paste(diagnostics$severity, collapse = ","),
  "ERROR,WARNING,NOTE"
)
add_result(
  "cran_response_register_complete",
  response_audit$ready_to_resubmit,
  response_audit$ready_to_resubmit,
  TRUE
)
add_result(
  "resubmission_sequence_valid",
  sequence_audit$valid,
  sequence_audit$valid,
  TRUE
)
add_result(
  "cran_comments_rendered",
  length(comments) >= 10L && any(grepl("R CMD check", comments, fixed = TRUE)),
  length(comments),
  "at least 10 lines with a check heading"
)

safe_api <- example_envs$ch32$audit_api_change(
  data.frame(
    name = c("fit_model", "predict_model"),
    signature = c("fit_model(x, y)", "predict_model(object, newdata)"),
    stringsAsFactors = FALSE
  ),
  data.frame(
    name = c("fit_model", "predict_model", "print_model"),
    signature = c(
      "fit_model(x, y)",
      "predict_model(object, newdata)",
      "print_model(object)"
    ),
    stringsAsFactors = FALSE
  ),
  deprecations = character()
)
breaking_api <- example_envs$ch32$audit_api_change(
  data.frame(
    name = c("fit_model", "predict_model"),
    signature = c("fit_model(x, y)", "predict_model(object, newdata)"),
    stringsAsFactors = FALSE
  ),
  data.frame(
    name = "fit_model",
    signature = "fit_model(x, y, weights)",
    stringsAsFactors = FALSE
  ),
  deprecations = character()
)
reverse_summary <- example_envs$ch32$summarize_reverse_dependencies(
  data.frame(
    package = c("downstreamA", "downstreamB"),
    status = c("PASS", "PASS"),
    stringsAsFactors = FALSE
  )
)
maintenance <- example_envs$ch32$maintenance_gate(list(
  api_reviewed = TRUE,
  deprecations_documented = TRUE,
  reverse_dependencies_checked = TRUE,
  news_updated = TRUE,
  security_contact_current = TRUE,
  maintainer_contact_current = TRUE,
  checks_passed = TRUE
))
add_result(
  "additive_api_change_allowed",
  safe_api$compatible,
  safe_api$compatible,
  TRUE
)
add_result(
  "unannounced_breaking_change_blocked",
  !breaking_api$compatible,
  breaking_api$compatible,
  FALSE
)
add_result(
  "reverse_dependency_gate",
  reverse_summary$gate_passed,
  reverse_summary$failed,
  0L
)
add_result(
  "maintenance_gate",
  maintenance$passed,
  maintenance$passed,
  TRUE
)
add_result(
  "version_increment_helper",
  identical(
    example_envs$ch32$suggest_version_increment("0.4.2", "minor"),
    "0.5.0"
  ),
  example_envs$ch32$suggest_version_increment("0.4.2", "minor"),
  "0.5.0"
)

prototype_after <- digest::digest(
  file = prototype_path,
  algo = "sha256",
  serialize = FALSE
)
add_result(
  "bernoulli_prototype_unchanged",
  identical(prototype_before, prototype_expected) &&
    identical(prototype_after, prototype_expected),
  prototype_after,
  prototype_expected
)

persistent_metadata <- file.exists(file.path(
  project_dir,
  "companion",
  "v0.1",
  "capstone-package",
  c("DESCRIPTION", "NAMESPACE")
))
add_result(
  "persistent_package_metadata_absent",
  !any(persistent_metadata),
  any(persistent_metadata),
  FALSE
)

all_passed <- all(vapply(results, function(x) isTRUE(x$passed), logical(1)))
generated_at <- format(Sys.time(), tz = "UTC", usetz = TRUE)
report <- list(
  schema_version = "1.0",
  project_version = "v0.1",
  run_id = run_id,
  generated_at_utc = generated_at,
  status = if (all_passed) "PASS" else "FAIL",
  scope = list(
    production_run = FALSE,
    network_access = FALSE,
    git_state_changed = FALSE,
    github_state_changed = FALSE,
    cran_submission_performed = FALSE,
    package_build_install_or_check_run = FALSE,
    persistent_package_tree_created = FALSE,
    sglasso_repository_modified = FALSE
  ),
  prototype = list(
    path = relative_path(prototype_path),
    sha256_before = prototype_before,
    sha256_after = prototype_after,
    unchanged = identical(prototype_before, prototype_after)
  ),
  sglasso_case = list(
    snapshot = snapshot,
    active_cran_name_conflict_detected = !sglasso_audit$clear,
    interpretation = paste(
      "The two packages are distinct; this local fixture records a name",
      "audit lesson and is not a live registry query."
    )
  ),
  diagnostics = list(
    count = nrow(diagnostics),
    response_register_ready = response_audit$ready_to_resubmit,
    sequence_valid = sequence_audit$valid
  ),
  maintenance = list(
    additive_api_compatible = safe_api$compatible,
    unannounced_breaking_change_rejected = !breaking_api$compatible,
    reverse_dependency_gate_passed = reverse_summary$gate_passed,
    maintenance_gate_passed = maintenance$passed
  ),
  results = results
)

report_path <- file.path(output_dir, "release_readiness_smoke.json")
write_json_atomic(report, report_path)

results_table <- data.frame(
  name = vapply(results, `[[`, character(1), "name"),
  passed = vapply(results, `[[`, logical(1), "passed"),
  stringsAsFactors = FALSE
)
results_path <- file.path(output_dir, "results.tsv")
utils::write.table(
  results_table,
  results_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE,
  fileEncoding = "UTF-8"
)

environment_path <- file.path(output_dir, "environment.txt")
environment_lines <- c(
  paste0("generated_at_utc=", generated_at),
  paste0("R.version.string=", R.version.string),
  paste0("platform=", R.version$platform),
  paste0("jsonlite=", as.character(utils::packageVersion("jsonlite"))),
  paste0("digest=", as.character(utils::packageVersion("digest"))),
  paste0("libpaths=", paste(.libPaths(), collapse = "|"))
)
writeLines(environment_lines, environment_path, useBytes = TRUE)

manifest_inputs <- c(example_paths, prototype_path, report_path, results_path,
                     environment_path)
manifest <- list(
  schema_version = "1.0",
  project_version = "v0.1",
  run_id = run_id,
  generated_at_utc = generated_at,
  files = lapply(manifest_inputs, function(path) {
    list(
      path = relative_path(path),
      bytes = unname(file.info(path)$size),
      sha256 = digest::digest(file = path, algo = "sha256", serialize = FALSE)
    )
  })
)
write_json_atomic(manifest, file.path(output_dir, "manifest.json"))

cat("Yayın hazırlığı duman sınaması: ", report$status, "\n", sep = "")
cat("Kayıt: ", output_dir, "\n", sep = "")
if (!all_passed) {
  quit(status = 1L)
}
