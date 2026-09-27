#include <R.h>
#include <Rinternals.h>
#include <R_ext/Rdynload.h>
#include <R_ext/Visibility.h>

extern void axpy_f(
    const int *n,
    const double *a,
    const double *x,
    const double *y,
    double *out);

extern SEXP axpy_call(SEXP a_sexp, SEXP x_sexp, SEXP y_sexp);

static R_NativePrimitiveArgType axpy_types[] = {
    INTSXP, REALSXP, REALSXP, REALSXP, REALSXP
};

static const R_CMethodDef c_methods[] = {
    {"axpy_f", (DL_FUNC) &axpy_f, 5, axpy_types},
    {NULL, NULL, 0, NULL}
};

static const R_CallMethodDef call_methods[] = {
    {"axpy_call", (DL_FUNC) &axpy_call, 3},
    {NULL, NULL, 0}
};

void attribute_visible R_init_nativepilot(DllInfo *dll) {
  R_registerRoutines(dll, c_methods, call_methods, NULL, NULL);
  R_useDynamicSymbols(dll, FALSE);
  R_forceSymbols(dll, TRUE);
}
