#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."),
                             mustWork = TRUE)

run_id <- Sys.getenv("BERNOULLI_RUNS_CHECK_ID", unset = "")
if (!nzchar(run_id)) {
  stop(
    paste(
      "BERNOULLI_RUNS_CHECK_ID zorunludur; örnek:",
      "v0.1-bernoulli-runs-package-01"
    ),
    call. = FALSE
  )
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop(
    "BERNOULLI_RUNS_CHECK_ID yalnızca güvenli ASCII karakterleri içerebilir.",
    call. = FALSE
  )
}

required_packages <- c(
  "digest", "jsonlite", "knitr", "rmarkdown", "roxygen2", "testthat"
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

package_dir <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "BernoulliRuns"
)
prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
required_files <- c(
  file.path(package_dir, "DESCRIPTION"),
  file.path(package_dir, "NAMESPACE"),
  prototype_path
)
if (any(!file.exists(required_files))) {
  stop("Paket ağacı, NAMESPACE veya dondurulmuş prototip eksik.",
       call. = FALSE)
}

expected_prototype_hash <- paste0(
  "ad2098c4b80cd72625ae894f547a76c1b7ab535e5089a3a68",
  "dfb3589ab36912c"
)
prototype_hash_before <- digest::digest(
  file = prototype_path,
  algo = "sha256",
  serialize = FALSE
)
if (!identical(prototype_hash_before, expected_prototype_hash)) {
  stop(
    "Dondurulmuş prototipin SHA-256 imzası değişmiş; işlem durduruldu.",
    call. = FALSE
  )
}

output_dir <- file.path(project_dir, "validation", "v0.1", run_id)
if (file.exists(output_dir)) {
  stop(
    "Doğrulama kimliği zaten var; üzerine yazılmadı: ", run_id,
    call. = FALSE
  )
}
log_dir <- file.path(output_dir, "logs")
build_dir <- file.path(output_dir, "build")
check_dir <- file.path(output_dir, "check")
library_dir <- file.path(output_dir, "library")
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(build_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(check_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(library_dir, recursive = TRUE, showWarnings = FALSE)

capture_to_file <- function(path, expression) {
  connection <- file(path, open = "wt", encoding = "UTF-8")
  sink(connection, type = "output")
  sink(connection, type = "message")
  on.exit({
    sink(type = "message")
    sink(type = "output")
    close(connection)
  }, add = TRUE)
  force(expression)
}

run_command <- function(label, command, arguments, working_directory) {
  log_path <- file.path(log_dir, paste0(label, ".log"))
  previous_directory <- getwd()
  on.exit(setwd(previous_directory), add = TRUE)
  setwd(working_directory)
  status <- system2(
    command,
    args = arguments,
    stdout = log_path,
    stderr = log_path,
    wait = TRUE
  )
  if (is.null(status)) {
    status <- 0L
  }
  list(
    label = label,
    status = as.integer(status),
    log = log_path,
    command = paste(c(command, arguments), collapse = " ")
  )
}

stage_results <- list()

roxygen_log <- file.path(log_dir, "roxygen.log")
capture_to_file(
  roxygen_log,
  roxygen2::roxygenise(package_dir, roclets = c("rd", "namespace"))
)
stage_results$roxygen <- list(
  label = "roxygen",
  status = 0L,
  log = roxygen_log,
  command = "roxygen2::roxygenise(..., roclets = c('rd', 'namespace'))"
)

r_files <- c(
  list.files(file.path(package_dir, "R"), full.names = TRUE,
             pattern = "[.]R$"),
  list.files(file.path(package_dir, "tests"), full.names = TRUE,
             recursive = TRUE, pattern = "[.]R$")
)
parse_log <- file.path(log_dir, "parse.log")
capture_to_file(parse_log, {
  for (path in sort(r_files)) {
    parse(path)
    cat("PASS", substring(path, nchar(package_dir) + 2L), "\n")
  }
})
stage_results$parse <- list(
  label = "parse",
  status = 0L,
  log = parse_log,
  command = "parse all package and test R files"
)

test_log <- file.path(log_dir, "testthat.log")
capture_to_file(
  test_log,
  testthat::test_local(
    package_dir,
    reporter = "summary",
    stop_on_failure = TRUE,
    stop_on_warning = TRUE
  )
)
stage_results$testthat <- list(
  label = "testthat",
  status = 0L,
  log = test_log,
  command = "testthat::test_local(..., stop_on_failure = TRUE)"
)

package_environment <- new.env(parent = baseenv())
for (path in sort(list.files(
  file.path(package_dir, "R"),
  full.names = TRUE,
  pattern = "[.]R$"
))) {
  sys.source(path, envir = package_environment, keep.source = TRUE)
}
prototype_environment <- new.env(parent = baseenv())
sys.source(prototype_path, envir = prototype_environment, keep.source = TRUE)

package_distribution <- get(
  "runs_distribution", envir = package_environment, inherits = FALSE
)
package_mean <- get("runs_mean", envir = package_environment, inherits = FALSE)
package_tail <- get("runs_tail", envir = package_environment, inherits = FALSE)
reference_distribution <- get(
  "runs_distribution_reference", envir = prototype_environment,
  inherits = FALSE
)
reference_mean <- get(
  "runs_mean_reference", envir = prototype_environment, inherits = FALSE
)
reference_tail <- get(
  "runs_tail_reference", envir = prototype_environment, inherits = FALSE
)

count_runs_independently <- function(x) {
  if (length(x) == 1L) {
    return(1L)
  }
  as.integer(1L + sum(x[-1L] != x[-length(x)]))
}

enumerate_pmf <- function(prob) {
  n <- length(prob)
  grid <- expand.grid(
    rep(list(c(0L, 1L)), n),
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  sequences <- as.matrix(grid)
  storage.mode(sequences) <- "integer"
  weights <- apply(sequences, 1L, function(x) {
    prod(ifelse(x == 1L, prob, 1 - prob))
  })
  run_counts <- apply(sequences, 1L, count_runs_independently)
  vapply(seq_len(n), function(r) {
    sum(weights[run_counts == r])
  }, numeric(1))
}

scientific_tolerance <- 1e-12
scientific_results <- data.frame(
  n = seq_len(8L),
  binary_sequences = 2^(seq_len(8L)),
  package_vs_prototype = NA_real_,
  package_vs_enumeration = NA_real_,
  mass_error = NA_real_,
  mean_vs_prototype = NA_real_,
  mean_vs_pmf = NA_real_,
  stringsAsFactors = FALSE
)

for (n in seq_len(8L)) {
  prob <- if (n == 1L) 0.37 else seq(0.12, 0.88, length.out = n)
  package_result <- package_distribution(prob)
  reference_result <- reference_distribution(prob)
  enumerated <- enumerate_pmf(prob)
  package_expectation <- package_mean(prob)
  reference_expectation <- reference_mean(prob)

  scientific_results$package_vs_prototype[n] <- max(abs(
    package_result$probability - reference_result$probability
  ))
  scientific_results$package_vs_enumeration[n] <- max(abs(
    package_result$probability - enumerated
  ))
  scientific_results$mass_error[n] <- abs(
    sum(package_result$probability) - 1
  )
  scientific_results$mean_vs_prototype[n] <- abs(
    package_expectation - reference_expectation
  )
  scientific_results$mean_vs_pmf[n] <- abs(
    package_expectation -
      sum(package_result$runs * package_result$probability)
  )
}

tail_x <- c(0L, 1L, 1L, 0L)
tail_prob <- c(0.15, 0.40, 0.75, 0.60)
tail_differences <- vapply(c("lower", "upper"), function(side) {
  abs(
    package_tail(tail_x, tail_prob, tail = side)$p.value -
      reference_tail(tail_x, tail_prob, tail = side)$p.value
  )
}, numeric(1))

scientific_values <- unlist(
  scientific_results[setdiff(names(scientific_results),
                             c("n", "binary_sequences"))],
  use.names = FALSE
)
scientific_passed <- all(scientific_values <= scientific_tolerance) &&
  all(tail_differences <= scientific_tolerance)
utils::write.table(
  scientific_results,
  file.path(output_dir, "scientific_validation.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
writeLines(
  c(
    paste0("lower_tail_difference: ", tail_differences[["lower"]]),
    paste0("upper_tail_difference: ", tail_differences[["upper"]]),
    paste0("tolerance: ", scientific_tolerance),
    paste0("status: ", if (scientific_passed) "PASS" else "FAIL")
  ),
  file.path(output_dir, "scientific_validation_summary.txt"),
  useBytes = TRUE
)
if (!scientific_passed) {
  stop("Bilimsel eşdeğerlik veya tam sayım kapısı başarısız.", call. = FALSE)
}
stage_results$scientific_validation <- list(
  label = "scientific_validation",
  status = 0L,
  log = file.path(output_dir, "scientific_validation_summary.txt"),
  command = "prototype equivalence and exhaustive enumeration for n = 1,...,8"
)

r_command <- file.path(R.home("bin"), "R")
rscript_command <- file.path(R.home("bin"), "Rscript")
stage_results$build <- run_command(
  "build",
  r_command,
  c("CMD", "build", shQuote(package_dir)),
  build_dir
)
if (stage_results$build$status != 0L) {
  stop("R CMD build başarısız; logs/build.log dosyasına bakın.",
       call. = FALSE)
}

tarballs <- list.files(
  build_dir,
  pattern = "^BernoulliRuns_[0-9.]+[.]tar[.]gz$",
  full.names = TRUE
)
if (length(tarballs) != 1L) {
  stop("Beklenen tek BernoulliRuns kaynak arşivi bulunamadı.", call. = FALSE)
}
tarball_path <- normalizePath(tarballs, mustWork = TRUE)

stage_results$install <- run_command(
  "install",
  r_command,
  c(
    "CMD", "INSTALL",
    paste0("--library=", shQuote(library_dir)),
    shQuote(tarball_path)
  ),
  output_dir
)
if (stage_results$install$status != 0L) {
  stop("Geçici kütüphaneye kurulum başarısız; logs/install.log dosyasına bakın.",
       call. = FALSE)
}

clean_script <- file.path(output_dir, "clean_session_smoke.R")
clean_result <- file.path(output_dir, "clean_session_smoke.txt")
writeLines(
  c(
    "args <- commandArgs(trailingOnly = TRUE)",
    ".libPaths(c(args[[1L]], .libPaths()))",
    "suppressPackageStartupMessages(library(BernoulliRuns))",
    "expected_exports <- c('count_runs', 'runs_distribution', 'runs_mean', 'runs_tail')",
    "stopifnot(all(expected_exports %in% getNamespaceExports('BernoulliRuns')))",
    "prob <- c(0.15, 0.40, 0.75, 0.60)",
    "distribution <- runs_distribution(prob)",
    "stopifnot(identical(names(distribution), c('runs', 'probability', 'cumulative')))",
    "stopifnot(abs(sum(distribution$probability) - 1) <= 1e-12)",
    "stopifnot(identical(count_runs(c(0, 1, 1, 0)), 3L))",
    "stopifnot(abs(runs_mean(prob) - sum(distribution$runs * distribution$probability)) <= 1e-12)",
    "stopifnot(inherits(runs_tail(c(0, 1, 1, 0), prob), 'runs_exact_tail'))",
    "writeLines('PASS', args[[2L]], useBytes = TRUE)"
  ),
  clean_script,
  useBytes = TRUE
)
stage_results$clean_session <- run_command(
  "clean-session",
  rscript_command,
  c("--vanilla", shQuote(clean_script), shQuote(library_dir),
    shQuote(clean_result)),
  output_dir
)
if (stage_results$clean_session$status != 0L ||
    !identical(readLines(clean_result, warn = FALSE), "PASS")) {
  stop("Temiz R oturumu sınaması başarısız.", call. = FALSE)
}

stage_results$check <- run_command(
  "check-as-cran",
  r_command,
  c("CMD", "check", "--as-cran", shQuote(tarball_path)),
  check_dir
)
check_log_candidates <- list.files(
  check_dir,
  pattern = "00check[.]log$",
  recursive = TRUE,
  full.names = TRUE
)
if (length(check_log_candidates) == 1L) {
  check_log <- check_log_candidates[[1L]]
} else {
  check_log <- stage_results$check$log
}
check_lines <- readLines(check_log, warn = FALSE)
check_status_line <- grep("^Status:", check_lines, value = TRUE)
if (length(check_status_line) != 1L) {
  check_status_line <- paste0(
    "Status: incomplete (command status ", stage_results$check$status, ")"
  )
}
extract_count <- function(label) {
  match <- regexec(paste0("([0-9]+) ", label), check_status_line)
  parts <- regmatches(check_status_line, match)[[1L]]
  if (length(parts) == 2L) as.integer(parts[[2L]]) else 0L
}
check_errors <- extract_count("ERROR")
check_warnings <- extract_count("WARNING")
check_notes <- extract_count("NOTE")
check_gate_passed <- stage_results$check$status == 0L &&
  check_errors == 0L && check_warnings == 0L

prototype_hash_after <- digest::digest(
  file = prototype_path,
  algo = "sha256",
  serialize = FALSE
)
prototype_unchanged <- identical(
  prototype_hash_before,
  prototype_hash_after
)
if (!prototype_unchanged) {
  stop("Doğrulama sırasında dondurulmuş prototip değişti.", call. = FALSE)
}

package_files <- list.files(
  package_dir,
  recursive = TRUE,
  full.names = TRUE,
  all.files = TRUE,
  no.. = TRUE
)
package_files <- sort(package_files[file.info(package_files)$isdir %in% FALSE])
package_relative_paths <- substring(package_files, nchar(package_dir) + 2L)
git_internal <- package_relative_paths == ".git" |
  startsWith(package_relative_paths, ".git/") |
  startsWith(package_relative_paths, ".git\\")
package_files <- package_files[!git_internal]
package_relative_paths <- package_relative_paths[!git_internal]
package_hashes <- vapply(package_files, function(path) {
  digest::digest(file = path, algo = "sha256", serialize = FALSE)
}, character(1))
package_source_signature <- digest::digest(
  paste(package_relative_paths, package_hashes, sep = "=", collapse = "\n"),
  algo = "sha256",
  serialize = FALSE
)

environment_path <- file.path(output_dir, "environment.txt")
writeLines(
  c(
    paste0("run_id: ", run_id),
    paste0("generated_at_utc: ", format(Sys.time(), tz = "UTC", usetz = TRUE)),
    paste0("R: ", R.version.string),
    paste0("platform: ", R.version$platform),
    paste0("os: ", Sys.info()[["sysname"]], " ", Sys.info()[["release"]]),
    paste0("locale: ", Sys.getlocale()),
    paste0("libPaths: ", paste(.libPaths(), collapse = " | ")),
    vapply(required_packages, function(package) {
      paste0(package, ": ", as.character(utils::packageVersion(package)))
    }, character(1)),
    paste0("prototype_sha256_before: ", prototype_hash_before),
    paste0("prototype_sha256_after: ", prototype_hash_after),
    paste0("package_source_signature: ", package_source_signature),
    paste0("tarball_sha256: ", digest::digest(
      file = tarball_path, algo = "sha256", serialize = FALSE
    )),
    "production_run: false",
    "checkpoint_resume: not applicable to bounded package checks",
    "package_dependency_install_or_update: none",
    "temporary_candidate_install: isolated validation library only",
    "git_or_remote_mutation: none"
  ),
  environment_path,
  useBytes = TRUE
)

stage_table <- data.frame(
  stage = vapply(stage_results, `[[`, character(1), "label"),
  status = vapply(stage_results, `[[`, integer(1), "status"),
  command = vapply(stage_results, `[[`, character(1), "command"),
  log = vapply(stage_results, function(stage) {
    substring(normalizePath(stage$log, mustWork = TRUE),
              nchar(project_dir) + 2L)
  }, character(1)),
  stringsAsFactors = FALSE
)
utils::write.table(
  stage_table,
  file.path(output_dir, "stage_results.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

overall_passed <- all(stage_table$status == 0L) &&
  scientific_passed && prototype_unchanged && check_gate_passed
summary_path <- file.path(output_dir, "package_check_summary.json")
jsonlite::write_json(
  list(
    schema_version = "1.0",
    project_version = "v0.1",
    package = "BernoulliRuns",
    package_version = "0.1.0",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    status = if (overall_passed) {
      if (check_notes > 0L) "PASS_WITH_NOTES" else "PASS"
    } else {
      "FAIL"
    },
    scientific_contract = paste(
      "exact total run-count distribution for mutually independent",
      "Bernoulli trials with supplied position-specific probabilities"
    ),
    scientific_validation = list(
      status = if (scientific_passed) "PASS" else "FAIL",
      maximum_n = 8L,
      total_binary_sequences = sum(2^(seq_len(8L))),
      tolerance = scientific_tolerance,
      lower_tail_difference = unname(tail_differences[["lower"]]),
      upper_tail_difference = unname(tail_differences[["upper"]])
    ),
    prototype = list(
      expected_sha256 = expected_prototype_hash,
      sha256_before = prototype_hash_before,
      sha256_after = prototype_hash_after,
      unchanged = prototype_unchanged
    ),
    package_source_signature = package_source_signature,
    tarball = list(
      path = substring(tarball_path, nchar(project_dir) + 2L),
      bytes = unname(file.info(tarball_path)$size),
      sha256 = digest::digest(
        file = tarball_path, algo = "sha256", serialize = FALSE
      )
    ),
    check = list(
      command = stage_results$check$command,
      command_status = stage_results$check$status,
      status_line = check_status_line,
      errors = check_errors,
      warnings = check_warnings,
      notes = check_notes,
      gate_passed = check_gate_passed,
      log = substring(normalizePath(check_log, mustWork = TRUE),
                      nchar(project_dir) + 2L)
    ),
    scope = list(
      production_run = FALSE,
      native_code_added = FALSE,
      dependency_install_or_update = "none",
      temporary_candidate_install = TRUE,
      git_or_remote_mutation = "none"
    ),
    stages = stage_table
  ),
  summary_path,
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}
validation_files <- list.files(
  output_dir,
  recursive = TRUE,
  full.names = TRUE,
  all.files = TRUE,
  no.. = TRUE
)
validation_files <- validation_files[
  file.info(validation_files)$isdir %in% FALSE
]
manifest_path <- file.path(output_dir, "manifest.json")
manifest_files <- sort(unique(c(
  package_files,
  prototype_path,
  script_path,
  validation_files[normalizePath(validation_files, mustWork = TRUE) !=
                     normalizePath(manifest_path, mustWork = FALSE)]
)))
manifest_entries <- lapply(manifest_files, function(path) {
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
    package = "BernoulliRuns",
    package_version = "0.1.0",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    scientific_signature = paste(
      "exact total run-count distribution; mutually independent",
      "position-specific Bernoulli trials; frozen reference unchanged"
    ),
    package_source_signature = package_source_signature,
    files = manifest_entries
  ),
  manifest_path,
  pretty = TRUE,
  auto_unbox = TRUE
)

cat("BernoulliRuns paket doğrulaması:",
    if (overall_passed) "PASS" else "FAIL", "\n")
cat("Bilimsel eşdeğerlik ve n=1,...,8 tam sayım:",
    if (scientific_passed) "PASS" else "FAIL", "\n")
cat("Prototip değişmedi:", prototype_unchanged, "\n")
cat("R CMD check:", check_status_line, "\n")
cat("Kaynak arşivi:", tarball_path, "\n")
cat("Kayıt:", output_dir, "\n")
if (!overall_passed) {
  quit(status = 1L, save = "no")
}
