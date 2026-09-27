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

required_packages <- c("knitr", "jsonlite", "renv")
missing_packages <- required_packages[!vapply(
  required_packages,
  requireNamespace,
  quietly = TRUE,
  FUN.VALUE = logical(1)
)]
if (length(missing_packages)) {
  stop(
    "Bölüm 17 örneği için kurulu paketler gerekli: ",
    paste(missing_packages, collapse = ", "),
    ". Otomatik kurulum yapılmadı.",
    call. = FALSE
  )
}

summary_path <- Sys.getenv("RBOOK_CH16_SUMMARY_PATH", unset = "")
if (!nzchar(summary_path) || !file.exists(summary_path)) {
  stop("Geçerli RBOOK_CH16_SUMMARY_PATH zorunludur.", call. = FALSE)
}
summary_path <- normalizePath(summary_path, mustWork = TRUE)

output_dir <- Sys.getenv("RBOOK_CH17_OUTPUT_DIR", unset = "")
if (!nzchar(output_dir)) {
  output_dir <- file.path(tempdir(), "rbook-ch17-report-v0.1")
}
if (file.exists(output_dir)) {
  stop("Bölüm 17 çıktı dizini zaten var; üzerine yazılmadı: ", output_dir,
       call. = FALSE)
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

simulation_summary <- utils::read.delim(
  summary_path,
  check.names = FALSE,
  stringsAsFactors = FALSE
)
expected_names <- c(
  "runs", "exact_probability", "estimated_probability",
  "monte_carlo_standard_error", "replications"
)
if (!identical(names(simulation_summary), expected_names) ||
    nrow(simulation_summary) != 4L ||
    !identical(as.integer(simulation_summary$runs), 1:4) ||
    any(simulation_summary$replications != 64L)) {
  stop("Bölüm 16 özeti beklenen şemayı veya boyutu taşımıyor.",
       call. = FALSE)
}

derived_summary_path <- file.path(
  output_dir, "simulasyon_ozeti_turetilmis_v0_1.tsv"
)
report_path <- file.path(output_dir, "arastirma_raporu_v0_1.md")
environment_path <- file.path(output_dir, "environment_v0_1.txt")
metadata_path <- file.path(output_dir, "report_metadata_v0_1.json")

utils::write.table(
  simulation_summary,
  derived_summary_path,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

workflow_contract <- data.frame(
  stage = c("Girdi", "İşleme", "Çıktı"),
  artifact = c(
    basename(summary_path),
    "arastirma_projesinin_yasami.R",
    basename(report_path)
  ),
  rule = c(
    "Salt okunur; değiştirilmez",
    "Şema ve boyut denetlenir",
    "Yeni sürümlü dizine yazılır"
  ),
  stringsAsFactors = FALSE
)
software_versions <- data.frame(
  component = c("R", required_packages),
  version = c(
    paste(R.version$major, R.version$minor, sep = "."),
    vapply(required_packages, function(package) {
      as.character(utils::packageVersion(package))
    }, character(1))
  ),
  stringsAsFactors = FALSE
)

template_path <- file.path(
  project_dir, "companion", "v0.1", "examples", "ch17",
  "arastirma_raporu.Rmd"
)
report_environment <- new.env(parent = globalenv())
report_environment$simulation_summary <- simulation_summary
report_environment$workflow_contract <- workflow_contract
report_environment$software_versions <- software_versions
knitr::knit(
  input = template_path,
  output = report_path,
  envir = report_environment,
  quiet = TRUE,
  encoding = "UTF-8"
)

environment_lines <- c(
  paste0("R: ", R.version.string),
  paste0("platform: ", R.version$platform),
  paste0("locale: ", Sys.getlocale()),
  paste0("libPaths: ", paste(.libPaths(), collapse = " | ")),
  vapply(required_packages, function(package) {
    paste0(package, ": ", as.character(utils::packageVersion(package)))
  }, character(1)),
  "renv_mutation_calls: none",
  "git_mutation_calls: none"
)
writeLines(environment_lines, environment_path, useBytes = TRUE)

jsonlite::write_json(
  list(
    schema_version = "1.0",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    source_summary = summary_path,
    source_summary_bytes_before = unname(file.info(summary_path)$size),
    output_report = report_path,
    replications = 64L,
    production_run = FALSE,
    renv_state_changed = FALSE,
    git_state_changed = FALSE
  ),
  metadata_path,
  pretty = TRUE,
  auto_unbox = TRUE
)

source_summary_after <- utils::read.delim(
  summary_path,
  check.names = FALSE,
  stringsAsFactors = FALSE
)
report_text <- paste(readLines(report_path, warn = FALSE, encoding = "UTF-8"),
                     collapse = "\n")
stopifnot(
  identical(simulation_summary, source_summary_after),
  all(file.exists(c(derived_summary_path, report_path, environment_path,
                    metadata_path))),
  all(file.info(c(derived_summary_path, report_path, environment_path,
                  metadata_path))$size > 0L),
  grepl("Simülasyon özeti", report_text, fixed = TRUE),
  grepl("monte_carlo_standard_error", report_text, fixed = TRUE),
  grepl("renv_mutation_calls: none", paste(environment_lines,
                                             collapse = "\n"),
        fixed = TRUE)
)

cat("Kaynak özet değişmedi: TRUE\n")
cat("knitr raporu:", basename(report_path), "\n")
cat("renv ve Git durumu değiştirilmedi: TRUE\n")

ch17_report_path <- report_path
ch17_result <- TRUE
