args_full <- commandArgs(trailingOnly = FALSE)
project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) stop("Betik yolu belirlenemedi.", call. = FALSE)
  script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
  project_dir <- normalizePath(file.path(dirname(script_path), "..", "..", "..", ".."), mustWork = TRUE)
}

source(
  file.path(project_dir, "companion", "v0.1", "capstone-package",
            "prototype", "bernoulli_runs_reference.R"),
  local = TRUE,
  encoding = "UTF-8"
)

yakalanan_hata <- tryCatch(
  runs_pmf_reference(c(0.20, NA_real_, 0.70)),
  runs_input_error = function(cnd) cnd
)

new_runs_size_warning <- function(n, limit) {
  structure(
    list(
      message = paste0("Öğretim eşiği aşıldı: n = ", n, ", eşik = ", limit),
      call = NULL,
      n = n,
      limit = limit
    ),
    class = c("runs_size_warning", "warning", "condition")
  )
}

warn_if_long_demo <- function(prob, limit = 4L) {
  prob <- validate_run_probabilities(prob)
  if (length(prob) > limit) {
    warning(new_runs_size_warning(length(prob), limit))
  }
  invisible(prob)
}

uyari_kaydi <- character()
withCallingHandlers(
  warn_if_long_demo(rep(0.5, 5L)),
  runs_size_warning = function(cnd) {
    uyari_kaydi <<- conditionMessage(cnd)
    invokeRestart("muffleWarning")
  }
)

stopifnot(
  inherits(yakalanan_hata, "runs_input_error"),
  identical(yakalanan_hata$argument, "prob"),
  length(uyari_kaydi) == 1L,
  grepl("n = 5", uyari_kaydi, fixed = TRUE)
)

cat("Hata sınıfı:", class(yakalanan_hata)[1L], "\n")
cat("Hatalı argüman:", yakalanan_hata$argument, "\n")
cat("Yakalanan uyarı:", uyari_kaydi, "\n")

ch10_result <- TRUE

