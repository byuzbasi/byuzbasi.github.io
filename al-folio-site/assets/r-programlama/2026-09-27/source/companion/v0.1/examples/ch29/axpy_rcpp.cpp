#include <Rcpp.h>

// [[Rcpp::export]]
Rcpp::NumericVector axpy_cpp(
    const double a,
    const Rcpp::NumericVector& x,
    const Rcpp::NumericVector& y) {
  const R_xlen_t n = x.size();
  if (y.size() != n) {
    Rcpp::stop("`x` and `y` must have equal lengths.");
  }

  Rcpp::NumericVector out(n);
  for (R_xlen_t i = 0; i < n; ++i) {
    out[i] = a * x[i] + y[i];
  }
  return out;
}
