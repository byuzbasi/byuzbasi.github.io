# Bölüm 28: kayıtlı .Call simgesi için doğrulayan R sarmalayıcı.

axpy_c_api <- function(a, x, y, native_symbol) {
  validated <- axpy_r(a, x, y)
  candidate <- .Call(
    native_symbol,
    as.double(a),
    as.double(x),
    as.double(y)
  )
  if (!is.double(candidate) || length(candidate) != length(validated)) {
    stop("C API çekirdeği dönüş sözleşmesini bozdu.", call. = FALSE)
  }
  candidate
}
