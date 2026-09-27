#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

run_id <- Sys.getenv("LANGUAGE_CORE_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop("LANGUAGE_CORE_RUN_ID zorunludur; örnek: v0.1-language-core-01",
       call. = FALSE)
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("LANGUAGE_CORE_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
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

prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
example_root <- file.path(project_dir, "companion", "v0.1", "examples")
example_paths <- c(
  ch06 = file.path(example_root, "ch06", "ifadeler_ve_akis.R"),
  ch07 = file.path(example_root, "ch07", "fonksiyon_tasarimi.R"),
  ch08 = file.path(example_root, "ch08", "ortamlar_ve_kapsam.R"),
  ch09 = file.path(example_root, "ch09", "tembel_degerlendirme.R"),
  ch10 = file.path(example_root, "ch10", "kosullar_ve_hata_ayiklama.R")
)
required_files <- c(prototype_path, example_paths)
if (any(!file.exists(required_files))) {
  stop("Dil çekirdeği prototipi veya bölüm örneklerinden en az biri eksik.",
       call. = FALSE)
}

test_tolerance <- 1e-12

enumerate_runs_pmf <- function(prob, count_runs) {
  n <- length(prob)
  if (n > 12L) {
    stop("Tam sayım yalnızca küçük duman sınaması için n <= 12 kabul eder.",
         call. = FALSE)
  }
  result <- numeric(n)
  for (code in 0:(2^n - 1)) {
    x <- as.integer(intToBits(code))[seq_len(n)]
    sequence_probability <- prod(ifelse(x == 1L, prob, 1 - prob))
    runs <- count_runs(x)
    result[runs] <- result[runs] + sequence_probability
  }
  result
}

run_prototype_tests <- function() {
  prototype_env <- new.env(parent = baseenv())
  error_message <- NULL
  visible_output <- tryCatch(
    utils::capture.output({
      sys.source(prototype_path, envir = prototype_env, keep.source = TRUE)

      capture_error <- function(expr) {
        tryCatch(
          {
            force(expr)
            NULL
          },
          error = function(e) e
        )
      }

      prob <- c(0.10, 0.30, 0.80, 0.60, 0.20)
      pmf_dp <- prototype_env$runs_pmf_reference(prob)
      pmf_enum <- enumerate_runs_pmf(
        prob,
        prototype_env$count_runs_reference
      )

      iid_prob <- rep(0.35, 7L)
      iid_pmf <- prototype_env$runs_pmf_reference(iid_prob)
      iid_mean_from_pmf <- sum(seq_along(iid_pmf) * iid_pmf)
      iid_mean_closed <- 1 + 2 * (length(iid_prob) - 1) * 0.35 * 0.65

      degenerate_prob <- c(0, 0, 1, 1, 0)
      degenerate_pmf <- prototype_env$runs_pmf_reference(degenerate_prob)
      invalid_errors <- list(
        empty_prob = capture_error(
          prototype_env$runs_pmf_reference(numeric())
        ),
        dimensional_prob = capture_error(
          prototype_env$runs_pmf_reference(matrix(0.5, nrow = 1L))
        ),
        missing_prob = capture_error(
          prototype_env$runs_pmf_reference(c(0.2, NA_real_))
        ),
        infinite_prob = capture_error(
          prototype_env$runs_pmf_reference(c(0.2, Inf))
        ),
        out_of_range_prob = capture_error(
          prototype_env$runs_pmf_reference(c(0.2, 1.1))
        ),
        invalid_sequence = capture_error(
          prototype_env$count_runs_reference(c(0L, 2L, 1L))
        ),
        unequal_lengths = capture_error(
          prototype_env$runs_tail_reference(
            c(0L, 1L),
            c(0.2, 0.5, 0.8),
            tail = "lower"
          )
        )
      )
      tail_result <- prototype_env$runs_tail_reference(
        c(0L, 0L, 1L, 1L, 0L),
        prob,
        tail = "upper"
      )
      singleton_pmf <- prototype_env$runs_pmf_reference(0.4)

      stopifnot(
        all(pmf_dp >= 0),
        abs(sum(pmf_dp) - 1) < test_tolerance,
        max(abs(unname(pmf_dp) - pmf_enum)) < test_tolerance,
        abs(iid_mean_from_pmf - iid_mean_closed) < test_tolerance,
        abs(prototype_env$runs_mean_reference(iid_prob) -
              iid_mean_closed) < test_tolerance,
        abs(sum(degenerate_pmf) - 1) < test_tolerance,
        identical(unname(which(degenerate_pmf == 1)), 3L),
        identical(unname(singleton_pmf), 1),
        all(vapply(
          invalid_errors,
          inherits,
          logical(1),
          what = "runs_input_error"
        )),
        identical(invalid_errors$invalid_sequence$argument, "x"),
        identical(invalid_errors$unequal_lengths$argument, "x"),
        all(vapply(
          invalid_errors[grep("prob", names(invalid_errors))],
          function(cnd) identical(cnd$argument, "prob"),
          logical(1)
        )),
        tail_result$p.value >= 0,
        tail_result$p.value <= 1
      )

      cat("DP ve tam sayım en büyük fark:",
          sprintf("%.3e", max(abs(unname(pmf_dp) - pmf_enum))), "\n")
      cat("Olasılık kütlesi toplamı:",
          sprintf("%.12f", sum(pmf_dp)), "\n")
      cat("IID özel durum ortalama farkı:",
          sprintf("%.3e", abs(iid_mean_from_pmf - iid_mean_closed)), "\n")
      cat("Dejenere dizinin koşu sayısı:",
          which(degenerate_pmf == 1), "\n")
      cat("Geçersiz girdi kapısı sayısı:", length(invalid_errors), "\n")
      cat("Özel hata sınıfları:",
          paste(unique(vapply(invalid_errors, function(cnd) {
            class(cnd)[1L]
          }, character(1))), collapse = ", "), "\n")
    }),
    error = function(e) {
      error_message <<- conditionMessage(e)
      character()
    }
  )

  passed <- is.null(error_message)
  output_path <- file.path(output_dir, "outputs", "prototype.txt")
  writeLines(
    c(
      paste0("status: ", if (passed) "PASS" else "FAIL"),
      if (!is.null(error_message)) paste0("error: ", error_message),
      visible_output
    ),
    output_path,
    useBytes = TRUE
  )
  list(label = "prototype", passed = passed, error = error_message,
       output_path = output_path)
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
    exists(result_name, envir = example_env, inherits = FALSE) &&
    isTRUE(get(result_name, envir = example_env, inherits = FALSE))
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
  } else{
    Sys.setenv(RBOOK_PROJECT_DIR = old_project_dir)
  }
}, add = TRUE)
Sys.setenv(RBOOK_PROJECT_DIR = project_dir)

run_results <- c(
  list(run_prototype_tests()),
  lapply(names(example_paths), function(label) {
    run_example(label, example_paths[[label]])
  })
)

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
  file.path(output_dir, "language_core_smoke.tsv"),
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
  paste0("jsonlite: ", as.character(utils::packageVersion("jsonlite"))),
  paste0("digest: ", as.character(utils::packageVersion("digest"))),
  paste0("test_tolerance: ", format(test_tolerance, scientific = TRUE))
)
writeLines(environment_lines, file.path(output_dir, "environment.txt"),
           useBytes = TRUE)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}

result_paths <- c(
  file.path(output_dir, "language_core_smoke.tsv"),
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
      "exact run-count distribution for independent Bernoulli trials",
      "with externally supplied position-specific probabilities"
    ),
    work_unit = "one reference-kernel gate plus one example per chapter",
    total_work_units = nrow(result_table),
    test_tolerance = test_tolerance,
    results = result_table,
    files = manifest_entries
  ),
  file.path(output_dir, "language_core_smoke.json"),
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

print(result_table, row.names = FALSE)
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
