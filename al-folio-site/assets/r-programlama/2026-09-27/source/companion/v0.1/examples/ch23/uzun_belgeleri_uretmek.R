# Bölüm 23: paket ağacı oluşturmadan çevrimdışı uzun belge örmek.

project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
output_dir <- Sys.getenv("RBOOK_CH23_OUTPUT_DIR", unset = "")
if (!nzchar(project_dir) || !nzchar(output_dir)) {
  stop("RBOOK_PROJECT_DIR ve RBOOK_CH23_OUTPUT_DIR zorunludur.",
       call. = FALSE)
}
project_dir <- normalizePath(project_dir, mustWork = TRUE)

if (!requireNamespace("knitr", quietly = TRUE)) {
  stop("Kurulu knitr paketi gereklidir; otomatik kurulum yapılmadı.",
       call. = FALSE)
}
if (file.exists(output_dir)) {
  stop("Bölüm 23 çıktı dizini zaten var; üzerine yazılmadı.", call. = FALSE)
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

template_path <- file.path(
  project_dir, "companion", "v0.1", "examples", "ch23",
  "paket_rehberi.Rmd"
)
if (!file.exists(template_path)) {
  stop("Bölüm 23 uzun belge kaynağı bulunamadı.", call. = FALSE)
}

template_text <- paste(
  readLines(template_path, warn = FALSE, encoding = "UTF-8"),
  collapse = "\n"
)
network_or_install_call <- grepl(
  "download[.]file|install[.]packages|https?://",
  template_text,
  perl = TRUE
)
if (network_or_install_call) {
  stop("Uzun belge çevrimdışı öğretim sözleşmesini ihlal ediyor.",
       call. = FALSE)
}

render_environment <- new.env(parent = baseenv())
rendered_path <- file.path(output_dir, "paket_rehberi.md")
knitr::knit(
  input = template_path,
  output = rendered_path,
  quiet = TRUE,
  envir = render_environment,
  encoding = "UTF-8"
)

rendered_text <- paste(
  readLines(rendered_path, warn = FALSE, encoding = "UTF-8"),
  collapse = "\n"
)
required_phrases <- c(
  "Belgenin amacı", "kesin koşu sayısı dağılımı", "Çıkarımsal sınır",
  "README", "vignette", "CITATION", "NEWS", "package site"
)

document_roles <- data.frame(
  artifact = c("README", "vignette", "CITATION", "NEWS", "package site"),
  executable_code_expected = c(TRUE, TRUE, FALSE, FALSE, TRUE),
  release_specific = c(FALSE, FALSE, FALSE, TRUE, FALSE),
  stringsAsFactors = FALSE
)

ch23_result <- file.exists(rendered_path) &&
  all(vapply(
    required_phrases,
    grepl,
    x = rendered_text,
    fixed = TRUE,
    FUN.VALUE = logical(1)
  )) &&
  nrow(document_roles) == 5L

if (!isTRUE(ch23_result)) {
  stop("Bölüm 23 çevrimdışı uzun belge denetimi başarısız.",
       call. = FALSE)
}

ch23_rendered_path <- rendered_path
cat("Bölüm 23: çevrimdışı knitr belgesi üretildi ve doğrulandı.\n")
