#!/usr/bin/env Rscript

args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)
if (length(file_arg) != 1L) {
  stop("Betik yolu belirlenemedi.", call. = FALSE)
}

script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
project_dir <- normalizePath(file.path(dirname(script_path), ".."),
                             mustWork = TRUE)

run_id <- Sys.getenv("NATIVE_RUN_ID", unset = "")
if (!nzchar(run_id)) {
  stop("NATIVE_RUN_ID zorunludur; örnek: v0.1-part5-smoke-01",
       call. = FALSE)
}
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("NATIVE_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
       call. = FALSE)
}

required_packages <- c("Rcpp", "RcppArmadillo", "jsonlite", "digest")
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
prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
source_paths <- c(
  prototype = prototype_path,
  chapter25 = file.path(example_root, "ch25", "once_olcmek.R"),
  chapter26 = file.path(example_root, "ch26", "rcpp_ilk_cekirdek.R"),
  chapter27_r = file.path(example_root, "ch27", "rcpparmadillo_matris.R"),
  chapter27_cpp = file.path(
    example_root, "ch27", "rcpparmadillo_matris.cpp"
  ),
  chapter28_r = file.path(example_root, "ch28", "c_api_arayuzu.R"),
  chapter28_c = file.path(example_root, "ch28", "axpy_call.c"),
  axpy_reference = file.path(example_root, "ch29", "axpy_reference.R"),
  axpy_rcpp = file.path(example_root, "ch29", "axpy_rcpp.cpp"),
  axpy_fortran = file.path(example_root, "ch29", "axpy_fortran.f90"),
  registration = file.path(example_root, "ch29", "registration_example.c")
)
if (any(!file.exists(source_paths))) {
  stop(
    "Kısım V örneklerinden en az biri eksik: ",
    paste(names(source_paths)[!file.exists(source_paths)], collapse = ", "),
    call. = FALSE
  )
}

prototype_hash_before <- digest::digest(
  file = prototype_path, algo = "sha256", serialize = FALSE
)

pilot_env <- new.env(parent = baseenv())
for (path in source_paths[c(
  "prototype", "chapter25", "axpy_reference", "chapter26",
  "chapter27_r", "chapter28_r"
)]) {
  sys.source(path, envir = pilot_env, keep.source = TRUE)
}

measurement_path <- file.path(output_dir, "measurement_smoke.tsv")
profile_path <- file.path(output_dir, "runs_reference.Rprof")
profile_summary_path <- file.path(output_dir, "profile_summary.tsv")
prob <- rep(c(0.25, 0.75), 24L)
measurement <- pilot_env$measure_runs_reference(prob, repetitions = 3L)
profile <- pilot_env$profile_runs_reference(
  prob, calls = 25L, profile_path = profile_path
)
utils::write.table(
  measurement,
  measurement_path,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
profile_table <- profile$sampled_functions
profile_table <- data.frame(
  function_name = rownames(profile_table),
  profile_table,
  row.names = NULL,
  check.names = FALSE,
  stringsAsFactors = FALSE
)
utils::write.table(
  profile_table,
  profile_summary_path,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)
measurement_passed <- nrow(measurement) == 3L &&
  identical(measurement$repetition, 1:3) &&
  all(is.finite(measurement$elapsed_seconds)) &&
  all(measurement$elapsed_seconds >= 0) &&
  all(measurement$output_identical) &&
  file.exists(profile_path) && file.info(profile_path)$size > 0L &&
  identical(profile$output, pilot_env$runs_pmf_reference(prob))

cost_components <- pilot_env$decompose_native_cost(1, 2, 3, 4)
cost_model_passed <- identical(unname(cost_components[["total"]]), 10) &&
  identical(pilot_env$compute_speedup(2, 1), 2)

capture_compile <- function(expression, log_path, label) {
  error_message <- NULL
  visible <- utils::capture.output(
    tryCatch(
      force(expression),
      error = function(cnd) {
        error_message <<- conditionMessage(cnd)
        NULL
      }
    ),
    type = "output"
  )
  passed <- is.null(error_message)
  writeLines(
    c(
      paste0("label: ", label),
      paste0("status: ", if (passed) "PASS" else "FAIL"),
      if (!is.null(error_message)) paste0("error: ", error_message),
      visible
    ),
    log_path,
    useBytes = TRUE
  )
  if (!passed) {
    stop(label, " derlemesi başarısız; günlük korundu.", call. = FALSE)
  }
  invisible(TRUE)
}

rcpp_cache <- tempfile(pattern = "rbook-rcpp-cache-")
rcpp_compile_log <- file.path(output_dir, "rcpp_compile.log")
capture_compile(
  pilot_env$compile_axpy_rcpp(
    source_paths[["axpy_rcpp"]], pilot_env, rcpp_cache
  ),
  rcpp_compile_log,
  "Rcpp AXPY"
)

armadillo_cache <- tempfile(pattern = "rbook-armadillo-cache-")
armadillo_compile_log <- file.path(output_dir, "rcpparmadillo_compile.log")
capture_compile(
  pilot_env$compile_matvec_arma(
    source_paths[["chapter27_cpp"]], pilot_env, armadillo_cache
  ),
  armadillo_compile_log,
  "RcppArmadillo matris-vektor"
)

build_dir <- tempfile(pattern = "rbook-native-build-")
dir.create(build_dir)
compiled_source_paths <- source_paths[c(
  "axpy_fortran", "chapter28_c", "registration"
)]
copied <- file.copy(compiled_source_paths, build_dir)
if (!all(copied)) {
  stop("C/Fortran kaynakları geçici dizine kopyalanamadı.", call. = FALSE)
}

old_dir <- setwd(build_dir)
on.exit(setwd(old_dir), add = TRUE)
dll_name <- paste0("nativepilot", .Platform$dynlib.ext)
r_executable <- file.path(R.home("bin"), "R")
compile_output <- system2(
  r_executable,
  c(
    "CMD", "SHLIB", "-o", dll_name,
    basename(source_paths[["axpy_fortran"]]),
    basename(source_paths[["chapter28_c"]]),
    basename(source_paths[["registration"]])
  ),
  stdout = TRUE,
  stderr = TRUE
)
compile_status <- attr(compile_output, "status")
if (is.null(compile_status)) compile_status <- 0L
native_compile_log <- file.path(output_dir, "native_compile.log")
writeLines(
  c(paste0("exit_status: ", compile_status), compile_output),
  native_compile_log,
  useBytes = TRUE
)
if (compile_status != 0L) {
  stop("C/Fortran derlemesi başarısız; günlük korundu.", call. = FALSE)
}

dll_path <- file.path(build_dir, dll_name)
dll <- dyn.load(dll_path)
on.exit(try(dyn.unload(dll_path), silent = TRUE), add = TRUE)

a <- 2
x <- c(1, 2, 3, 4)
y <- c(0.5, -0.5, 1.5, -1.5)
reference <- pilot_env$axpy_r(a, x, y)
cpp_result <- pilot_env$axpy_cpp(a, x, y)

call_symbol <- getNativeSymbolInfo("axpy_call", PACKAGE = dll)
c_api_result <- pilot_env$axpy_c_api(a, x, y, call_symbol)
fortran_symbol <- getNativeSymbolInfo("axpy_f", PACKAGE = dll)
fortran_result <- .C(
  fortran_symbol,
  n = as.integer(length(x)),
  a = as.double(a),
  x = as.double(x),
  y = as.double(y),
  out = double(length(x))
)$out

backend_values <- list(
  R = reference,
  Rcpp = as.double(cpp_result),
  C_API = as.double(c_api_result),
  Fortran = as.double(fortran_result)
)
max_abs_error <- vapply(
  backend_values,
  function(value) max(abs(value - reference)),
  numeric(1)
)
passed <- vapply(
  backend_values,
  function(value) identical(as.double(value), as.double(reference)),
  logical(1)
)
results <- data.frame(
  backend = names(backend_values),
  max_abs_error = unname(max_abs_error),
  passed = unname(passed),
  stringsAsFactors = FALSE
)
native_results_path <- file.path(output_dir, "native_smoke.tsv")
utils::write.table(
  results,
  native_results_path,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

matrix_example <- pilot_env$run_matvec_example(pilot_env$matvec_arma)
matrix_results <- data.frame(
  backend = c("R", "RcppArmadillo"),
  output = c(
    paste(matrix_example$reference, collapse = ","),
    paste(matrix_example$candidate, collapse = ",")
  ),
  max_abs_error = c(0, matrix_example$max_abs_error),
  passed = c(TRUE, matrix_example$exactly_equal),
  stringsAsFactors = FALSE
)
matrix_results_path <- file.path(output_dir, "matrix_smoke.tsv")
utils::write.table(
  matrix_results,
  matrix_results_path,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

c_type_error <- tryCatch(
  {
    .Call(call_symbol, as.double(a), as.integer(x), as.double(y))
    NULL
  },
  error = function(cnd) conditionMessage(cnd)
)
string_call_error <- tryCatch(
  {
    .Call(
      "axpy_call", as.double(a), as.double(x), as.double(y),
      PACKAGE = dll[["name"]]
    )
    NULL
  },
  error = function(cnd) conditionMessage(cnd)
)
matrix_dimension_error <- tryCatch(
  {
    pilot_env$matvec_arma(
      matrix(as.double(1:4), nrow = 2L),
      as.double(1:3)
    )
    NULL
  },
  error = function(cnd) conditionMessage(cnd)
)

registered <- getDLLRegisteredRoutines(dll)
registration_passed <-
  "axpy_call" %in% names(registered[[".Call"]]) &&
  "axpy_f" %in% names(registered[[".C"]]) &&
  identical(dll[["dynamicLookup"]], FALSE) &&
  !is.null(c_type_error) && grepl("double vectors", c_type_error, fixed = TRUE) &&
  !is.null(string_call_error) &&
  !is.null(matrix_dimension_error) &&
  grepl("column count", matrix_dimension_error, fixed = TRUE)

prototype_hash_after <- digest::digest(
  file = prototype_path, algo = "sha256", serialize = FALSE
)
prototype_unchanged <- identical(prototype_hash_before, prototype_hash_after)
forbidden_package_files <- file.path(
  project_dir,
  c(
    "DESCRIPTION", "NAMESPACE",
    "companion/v0.1/capstone-package/DESCRIPTION",
    "companion/v0.1/capstone-package/NAMESPACE"
  )
)
no_persistent_package_metadata <- all(!file.exists(forbidden_package_files))

rscript_executable <- file.path(R.home("bin"), "Rscript")
overwrite_output <- suppressWarnings(system2(
  rscript_executable,
  c("--vanilla", script_path),
  env = paste0("NATIVE_RUN_ID=", run_id),
  stdout = TRUE,
  stderr = TRUE
))
overwrite_status <- attr(overwrite_output, "status")
if (is.null(overwrite_status)) overwrite_status <- 0L
overwrite_refusal <- overwrite_status != 0L &&
  any(grepl("üzerine yazılmadı", overwrite_output, fixed = TRUE))
overwrite_log_path <- file.path(output_dir, "overwrite_refusal.log")
writeLines(
  c(paste0("exit_status: ", overwrite_status), overwrite_output),
  overwrite_log_path,
  useBytes = TRUE
)

config_value <- function(name) {
  value <- system2(
    r_executable,
    c("CMD", "config", name),
    stdout = TRUE,
    stderr = TRUE
  )
  status <- attr(value, "status")
  if (!is.null(status) && status != 0L) {
    return(paste0("unavailable (status ", status, ")"))
  }
  paste(value, collapse = " ")
}

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
  paste0("CC: ", config_value("CC")),
  paste0("CXX: ", config_value("CXX")),
  paste0("CXXSTD: ", config_value("CXXSTD")),
  paste0("FC: ", config_value("FC")),
  paste0("BLAS: ", config_value("BLAS_LIBS")),
  paste0("LAPACK: ", config_value("LAPACK_LIBS")),
  paste0("dynamic_library: ", basename(dll_path)),
  paste0("prototype_sha256_before: ", prototype_hash_before),
  paste0("prototype_sha256_after: ", prototype_hash_after),
  "production_benchmark: false",
  "actual_package_tree_created: false",
  "package_build_install_or_check: none",
  "package_install_or_update: none",
  "git_cloud_or_remote_mutation: none"
)
writeLines(environment_lines, environment_path, useBytes = TRUE)

all_passed <- all(results$passed) &&
  all(matrix_results$passed) &&
  measurement_passed &&
  cost_model_passed &&
  registration_passed &&
  overwrite_refusal &&
  prototype_unchanged &&
  no_persistent_package_metadata

result_json_path <- file.path(output_dir, "native_smoke.json")
jsonlite::write_json(
  list(
    schema_version = "2.0",
    project_version = "v0.1",
    run_id = run_id,
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    status = if (all_passed) "PASS" else "FAIL",
    scope = list(
      production_benchmark = FALSE,
      actual_package_tree_created = FALSE,
      package_build_install_or_check = "none",
      package_install_or_update = "none",
      remote_or_git_mutation = "none",
      local_compiler_evidence_only = TRUE
    ),
    scientific_contract = paste(
      "the independent position-specific Bernoulli exact run-count",
      "prototype was read-only and received no native implementation"
    ),
    prototype = list(
      sha256_before = prototype_hash_before,
      sha256_after = prototype_hash_after,
      unchanged = prototype_unchanged
    ),
    measurement = list(
      passed = measurement_passed,
      repetitions = nrow(measurement),
      profile_calls = profile$calls,
      sampled_function_rows = nrow(profile_table),
      speed_order_is_acceptance_gate = FALSE,
      cost_model_contract_passed = cost_model_passed
    ),
    axpy = list(
      equation = "z_i = a*x_i + y_i",
      exact_test_values = TRUE,
      results = results
    ),
    matrix_vector = list(
      equation = "y_i = sum_j A_ij*x_j",
      exact_test_values = TRUE,
      results = matrix_results
    ),
    interface_guards = list(
      registration_passed = registration_passed,
      dynamic_lookup_disabled = identical(dll[["dynamicLookup"]], FALSE),
      force_symbols_string_call_rejected = !is.null(string_call_error),
      c_type_error_observed = !is.null(c_type_error),
      matrix_dimension_error_observed = !is.null(matrix_dimension_error)
    ),
    overwrite_refusal = overwrite_refusal,
    persistent_package_metadata_absent = no_persistent_package_metadata,
    manifest = "manifest.json"
  ),
  result_json_path,
  pretty = TRUE,
  auto_unbox = TRUE,
  null = "null"
)

relative_path <- function(path) {
  normalized <- normalizePath(path, mustWork = TRUE)
  substring(normalized, nchar(project_dir) + 2L)
}
manifest_paths <- c(
  source_paths,
  script_path,
  measurement_path,
  profile_path,
  profile_summary_path,
  rcpp_compile_log,
  armadillo_compile_log,
  native_compile_log,
  native_results_path,
  matrix_results_path,
  overwrite_log_path,
  environment_path,
  result_json_path
)
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
    files = manifest_entries
  ),
  file.path(output_dir, "manifest.json"),
  pretty = TRUE,
  auto_unbox = TRUE
)

print(results, row.names = FALSE)
print(matrix_results, row.names = FALSE)
cat("Ölçüm şeması ve profil: ", if (measurement_passed) "PASS" else "FAIL",
    "\n", sep = "")
cat("Kayıt:", output_dir, "\n")
if (!all_passed) {
  quit(status = 1L, save = "no")
}
