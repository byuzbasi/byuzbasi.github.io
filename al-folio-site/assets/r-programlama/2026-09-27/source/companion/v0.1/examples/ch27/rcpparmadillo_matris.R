# Bölüm 27: R ve RcppArmadillo ile ortak matris-vektör sözleşmesi.

matvec_r <- function(matrix, vector) {
  if (!is.matrix(matrix) || !is.numeric(matrix)) {
    stop("`matrix` sayısal bir matris olmalıdır.", call. = FALSE)
  }
  if (!is.atomic(vector) || !is.numeric(vector) || !is.null(dim(vector))) {
    stop("`vector` boyutsuz sayısal bir vektör olmalıdır.", call. = FALSE)
  }
  if (!length(matrix) || !length(vector) ||
      nrow(matrix) < 1L || ncol(matrix) < 1L) {
    stop("Matris ve vektör boyutları pozitif olmalıdır.", call. = FALSE)
  }
  if (ncol(matrix) != length(vector)) {
    stop("Matrisin sütun sayısı vektör uzunluğuna eşit olmalıdır.",
         call. = FALSE)
  }
  if (anyNA(matrix) || anyNA(vector) ||
      any(!is.finite(matrix)) || any(!is.finite(vector))) {
    stop("Girdiler yalnızca sonlu değerler içermelidir.", call. = FALSE)
  }

  as.double(matrix %*% vector)
}

compile_matvec_arma <- function(cpp_path, target_environment,
                                cache_directory) {
  if (!requireNamespace("Rcpp", quietly = TRUE) ||
      !requireNamespace("RcppArmadillo", quietly = TRUE)) {
    stop(
      "Kurulu `Rcpp` ve `RcppArmadillo` paketleri gereklidir; kurulum yapılmadı.",
      call. = FALSE
    )
  }
  if (!file.exists(cpp_path)) {
    stop("RcppArmadillo C++ kaynağı bulunamadı.", call. = FALSE)
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
  invisible(target_environment$matvec_arma)
}

run_matvec_example <- function(compiled_function) {
  matrix <- matrix(c(1, 4, 2, 5, 3, 6), nrow = 2L, byrow = TRUE)
  vector <- c(2, -1, 3)
  reference <- matvec_r(matrix, vector)
  candidate <- as.double(compiled_function(matrix, vector))

  list(
    matrix = matrix,
    vector = vector,
    reference = reference,
    candidate = candidate,
    max_abs_error = max(abs(candidate - reference)),
    exactly_equal = identical(candidate, reference)
  )
}
