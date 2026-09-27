# Bölüm 29: AXPY işleminin saf-R referansı.

axpy_r <- function(a, x, y) {
  if (!is.numeric(a) || length(a) != 1L || !is.finite(a)) {
    stop("`a` tek ve sonlu bir sayısal değer olmalıdır.", call. = FALSE)
  }
  if (!is.numeric(x) || !is.numeric(y)) {
    stop("`x` ve `y` sayısal vektörler olmalıdır.", call. = FALSE)
  }
  if (length(x) != length(y)) {
    stop("`x` ve `y` eşit uzunlukta olmalıdır.", call. = FALSE)
  }
  if (length(x) == 0L) {
    stop("Pilot sözleşmede sıfır uzunluklu girdiye izin verilmez.", call. = FALSE)
  }
  if (any(!is.finite(x)) || any(!is.finite(y))) {
    stop("`x` ve `y` yalnızca sonlu değerler içermelidir.", call. = FALSE)
  }

  as.double(a) * as.double(x) + as.double(y)
}
