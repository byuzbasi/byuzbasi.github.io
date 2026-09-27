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

sayac <- 0L
kullanmayan <- function(x) 4L
iki_kere_kullanan <- function(x) x + x

sonuc_kullanilmadi <- kullanmayan({
  sayac <- sayac + 1L
  10L
})
sonuc_bir_kez <- iki_kere_kullanan({
  sayac <- sayac + 1L
  10L
})

olcek <- 10
olcegi_oku <- function(x = olcek) x
kapsam_sonuclari <- local({
  olcek <- 3
  c(varsayilan = olcegi_oku(), saglanan = olcegi_oku(olcek))
})

make_upper_tail <- function(prob) {
  prob <- validate_run_probabilities(prob)
  force(prob)
  function(x) runs_tail_reference(x, prob, tail = "upper")$p.value
}

prob <- c(0.20, 0.45, 0.70, 0.60)
upper_tail <- make_upper_tail(prob)
prob[1L] <- 0.99
kuyruk <- upper_tail(c(0L, 0L, 1L, 0L))

stopifnot(
  identical(sonuc_kullanilmadi, 4L),
  identical(sonuc_bir_kez, 20L),
  identical(sayac, 1L),
  identical(unname(kapsam_sonuclari), c(10, 3)),
  is.finite(kuyruk), kuyruk >= 0, kuyruk <= 1
)

cat("Yan etki sayısı:", sayac, "\n")
cat("Varsayılan ve sağlanan değer:",
    paste(kapsam_sonuclari, collapse = ", "), "\n")
cat("Dondurulmuş üst kuyruk:", sprintf("%.6f", kuyruk), "\n")

ch09_result <- TRUE

