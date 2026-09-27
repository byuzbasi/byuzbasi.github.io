# Bölüm 26: Bölüm 29'daki ortak AXPY C++ kaynağını geçici önbellekte derlemek.

compile_axpy_rcpp <- function(cpp_path, target_environment,
                              cache_directory) {
  if (!requireNamespace("Rcpp", quietly = TRUE)) {
    stop("Kurulu `Rcpp` paketi gereklidir; otomatik kurulum yapılmadı.",
         call. = FALSE)
  }
  if (!file.exists(cpp_path)) {
    stop("AXPY C++ kaynağı bulunamadı.", call. = FALSE)
  }
  if (!is.environment(target_environment)) {
    stop("`target_environment` bir R ortamı olmalıdır.", call. = FALSE)
  }
  if (file.exists(cache_directory)) {
    stop("Derleme önbelleği zaten var; üzerine yazılmadı.", call. = FALSE)
  }
  dir.create(cache_directory, recursive = TRUE, showWarnings = FALSE)

  Rcpp::sourceCpp(
    file = cpp_path,
    env = target_environment,
    cacheDir = cache_directory,
    rebuild = TRUE,
    showOutput = FALSE,
    verbose = FALSE
  )
  invisible(target_environment$axpy_cpp)
}

run_axpy_rcpp_example <- function(a, x, y, reference_function,
                                  compiled_function) {
  reference <- reference_function(a, x, y)
  candidate <- compiled_function(a, as.double(x), as.double(y))
  error <- max(abs(as.double(candidate) - reference))

  list(
    reference = reference,
    candidate = as.double(candidate),
    max_abs_error = error,
    exactly_equal = identical(as.double(candidate), as.double(reference))
  )
}
