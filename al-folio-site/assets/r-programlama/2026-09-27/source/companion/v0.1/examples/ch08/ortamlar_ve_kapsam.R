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

make_runs_engine <- function(prob) {
  prob <- validate_run_probabilities(prob)
  force(prob)
  cache <- new.env(parent = emptyenv())
  calculations <- 0L

  function(action = c("distribution", "mean", "status"), refresh = FALSE) {
    action <- match.arg(action)
    if (action == "status") {
      return(list(cached = exists("pmf", cache, inherits = FALSE),
                  calculations = calculations))
    }
    if (!is.logical(refresh) || length(refresh) != 1L || is.na(refresh)) {
      abort_runs_input("`refresh` tek ve eksiksiz mantıksal değer olmalıdır.",
                       "refresh")
    }
    if (refresh || !exists("pmf", cache, inherits = FALSE)) {
      cache$pmf <- runs_pmf_reference(prob)
      calculations <<- calculations + 1L
    }
    if (action == "mean") {
      return(sum(seq_along(cache$pmf) * cache$pmf))
    }
    data.frame(
      runs = seq_along(cache$pmf),
      probability = unname(cache$pmf),
      stringsAsFactors = FALSE
    )
  }
}

engine_a <- make_runs_engine(c(0.20, 0.45, 0.70, 0.60))
engine_b <- make_runs_engine(c(0.50, 0.50, 0.50, 0.50))

dagilim_a <- engine_a("distribution")
ortalama_a <- engine_a("mean")
durum_a <- engine_a("status")
durum_b <- engine_b("status")
yenilenmis_dagilim_a <- engine_a("distribution", refresh = TRUE)
yenilenmis_a <- engine_a("status")

stopifnot(
  durum_a$cached,
  identical(durum_a$calculations, 1L),
  !durum_b$cached,
  identical(durum_b$calculations, 0L),
  identical(yenilenmis_a$calculations, 2L),
  identical(yenilenmis_dagilim_a, dagilim_a),
  abs(sum(dagilim_a$probability) - 1) < 1e-12,
  abs(ortalama_a - runs_mean_reference(c(0.20, 0.45, 0.70, 0.60))) < 1e-12
)

cat("A motoru hesap sayısı:", durum_a$calculations, "\n")
cat("B motorunda önbellek var mı:", durum_b$cached, "\n")
cat("Yenileme sonrası A hesap sayısı:", yenilenmis_a$calculations, "\n")

ch08_result <- TRUE
