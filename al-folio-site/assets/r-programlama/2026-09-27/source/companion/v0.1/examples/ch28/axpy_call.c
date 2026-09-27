#define R_NO_REMAP
#include <R.h>
#include <Rinternals.h>
#include <R_ext/Arith.h>
#include <R_ext/Utils.h>

SEXP axpy_call(SEXP a_sexp, SEXP x_sexp, SEXP y_sexp) {
  if (TYPEOF(a_sexp) != REALSXP || XLENGTH(a_sexp) != 1) {
    Rf_error("`a` must be a double vector of length one.");
  }
  if (!R_FINITE(REAL(a_sexp)[0])) {
    Rf_error("`a` must be finite.");
  }
  if (TYPEOF(x_sexp) != REALSXP || TYPEOF(y_sexp) != REALSXP) {
    Rf_error("`x` and `y` must be double vectors.");
  }

  const R_xlen_t n = XLENGTH(x_sexp);
  if (n == 0) {
    Rf_error("Zero-length inputs are not allowed by the pilot contract.");
  }
  if (XLENGTH(y_sexp) != n) {
    Rf_error("`x` and `y` must have equal lengths.");
  }

  const double a = REAL(a_sexp)[0];
  const double *x = REAL(x_sexp);
  const double *y = REAL(y_sexp);
  for (R_xlen_t i = 0; i < n; ++i) {
    if (!R_FINITE(x[i]) || !R_FINITE(y[i])) {
      Rf_error("`x` and `y` must contain only finite values.");
    }
  }

  SEXP out_sexp = PROTECT(Rf_allocVector(REALSXP, n));
  double *out = REAL(out_sexp);
  for (R_xlen_t i = 0; i < n; ++i) {
    out[i] = a * x[i] + y[i];
    if ((i & 65535) == 0) {
      R_CheckUserInterrupt();
    }
  }

  UNPROTECT(1);
  return out_sexp;
}
