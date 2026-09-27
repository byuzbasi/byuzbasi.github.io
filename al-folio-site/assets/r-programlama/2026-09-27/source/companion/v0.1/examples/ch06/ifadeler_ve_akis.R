args_full <- commandArgs(trailingOnly = FALSE)
project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) {
    stop("Betik yolu belirlenemedi.", call. = FALSE)
  }
  script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
  project_dir <- normalizePath(
    file.path(dirname(script_path), "..", "..", "..", ".."),
    mustWork = TRUE
  )
}

source(
  file.path(
    project_dir,
    "companion", "v0.1", "capstone-package", "prototype",
    "bernoulli_runs_reference.R"
  ),
  local = TRUE,
  encoding = "UTF-8"
)

prob <- c(0.20, 0.45, 0.70, 0.60)
gozlem <- c(0L, 0L, 1L, 0L)

olasilik_turu <- if (all(prob == prob[1L])) {
  "ortak"
} else {
  "konuma göre değişen"
}

manuel_kosu <- 1L
if (length(gozlem) > 1L) {
  for (i in 2L:length(gozlem)) {
    if (gozlem[i] != gozlem[i - 1L]) {
      manuel_kosu <- manuel_kosu + 1L
    }
  }
}

pmf <- runs_pmf_reference(prob)
beklenen <- runs_mean_reference(prob)

stopifnot(
  identical(olasilik_turu, "konuma göre değişen"),
  identical(manuel_kosu, 3L),
  identical(manuel_kosu, count_runs_reference(gozlem)),
  abs(sum(pmf) - 1) < 1e-12,
  abs(sum(seq_along(pmf) * pmf) - beklenen) < 1e-12
)

cat("Olasılık yapısı:", olasilik_turu, "\n")
cat("Gözlenen koşu sayısı:", manuel_kosu, "\n")
cat("Olasılık kütlesinin toplamı:", sprintf("%.12f", sum(pmf)), "\n")
cat("Beklenen koşu sayısı:", sprintf("%.6f", beklenen), "\n")

ch06_result <- TRUE

