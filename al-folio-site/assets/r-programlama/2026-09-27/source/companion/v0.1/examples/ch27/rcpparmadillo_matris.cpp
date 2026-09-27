#include <RcppArmadillo.h>

// [[Rcpp::depends(RcppArmadillo)]]

// [[Rcpp::export]]
Rcpp::NumericVector matvec_arma(
    const arma::mat& matrix,
    const arma::vec& vector) {
  if (matrix.n_rows == 0 || matrix.n_cols == 0 || vector.n_elem == 0) {
    Rcpp::stop("Matrix and vector dimensions must be positive.");
  }
  if (matrix.n_cols != vector.n_elem) {
    Rcpp::stop("The matrix column count must equal the vector length.");
  }

  Rcpp::checkUserInterrupt();
  arma::vec result = matrix * vector;
  return Rcpp::wrap(result);
}
