# Bölüm 5: göreli yollarla güvenli dosya okuma ve ayrı çıktı üretme.

bul_ornek_dizini <- function() {
  override <- Sys.getenv("RBOOK_CH05_SCRIPT_DIR", unset = "")
  if (nzchar(override)) {
    return(normalizePath(override, winslash = "/", mustWork = TRUE))
  }

  args_full <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) {
    stop(
      "Betik dizini bulunamadı; dosyayı Rscript ile çalıştırın veya ",
      "RBOOK_CH05_SCRIPT_DIR değişkenini tanımlayın.",
      call. = FALSE
    )
  }

  script_path <- normalizePath(
    sub("^--file=", "", file_arg),
    winslash = "/",
    mustWork = TRUE
  )
  dirname(script_path)
}

ornek_dizini <- bul_ornek_dizini()
girdi_yolu <- file.path(ornek_dizini, "data", "ogrenciler_utf8.csv")
if (!file.exists(girdi_yolu)) {
  stop("Beklenen sentetik girdi bulunamadı: ", girdi_yolu, call. = FALSE)
}

ogrenciler <- utils::read.table(
  file = girdi_yolu,
  header = TRUE,
  sep = ",",
  dec = ".",
  quote = "\"",
  na.strings = "NA",
  comment.char = "",
  stringsAsFactors = FALSE,
  check.names = FALSE,
  fileEncoding = "UTF-8"
)

beklenen_sutunlar <- c("ogrenci_id", "ad", "puan", "grup")
if (!identical(names(ogrenciler), beklenen_sutunlar)) {
  stop("Girdi şeması beklenen sütunlarla eşleşmiyor.", call. = FALSE)
}

gruplar <- sort(unique(ogrenciler$grup))
gozlenen_n <- vapply(
  gruplar,
  function(g) sum(!is.na(ogrenciler$puan[ogrenciler$grup == g])),
  integer(1)
)
ortalama <- vapply(
  gruplar,
  function(g) mean(ogrenciler$puan[ogrenciler$grup == g], na.rm = TRUE),
  numeric(1)
)
ozet <- data.frame(
  grup = gruplar,
  gozlenen_n = unname(gozlenen_n),
  ortalama_puan = unname(ortalama),
  stringsAsFactors = FALSE
)

cikti_override <- Sys.getenv("RBOOK_CH05_OUTPUT_DIR", unset = "")
cikti_dizini <- if (nzchar(cikti_override)) {
  cikti_override
} else {
  tempfile(pattern = "r-kitap-ch05-")
}
dir.create(cikti_dizini, recursive = TRUE, showWarnings = FALSE)

cikti_yolu <- file.path(cikti_dizini, "grup_ozeti.csv")
if (file.exists(cikti_yolu)) {
  stop("Çıktının üzerine yazılmadı: ", cikti_yolu, call. = FALSE)
}

utils::write.table(
  ozet,
  file = cikti_yolu,
  sep = ",",
  dec = ".",
  quote = TRUE,
  qmethod = "double",
  row.names = FALSE,
  col.names = TRUE,
  fileEncoding = "UTF-8"
)

yazilan_ozet <- utils::read.table(
  file = cikti_yolu,
  header = TRUE,
  sep = ",",
  dec = ".",
  quote = "\"",
  stringsAsFactors = FALSE,
  check.names = FALSE,
  fileEncoding = "UTF-8"
)

stopifnot(
  nrow(ogrenciler) == 4L,
  identical(ogrenciler$ad, c("Çağla", "İpek", "Ömer", "Şule")),
  identical(is.na(ogrenciler$puan), c(FALSE, TRUE, FALSE, FALSE)),
  identical(ozet$gozlenen_n, c(2L, 1L)),
  isTRUE(all.equal(ozet$ortalama_puan, c(84.75, 84.5))),
  identical(yazilan_ozet, ozet)
)

cat("Okunan satır sayısı:", nrow(ogrenciler), "\n")
cat("Eksik puan sayısı:", sum(is.na(ogrenciler$puan)), "\n")
print(ozet, row.names = FALSE)
cat("Kaynak girdinin üzerine yazılmadı: TRUE\n")

ch05_result <- list(
  data = ogrenciler,
  summary = ozet,
  input_path = normalizePath(girdi_yolu, winslash = "/", mustWork = TRUE),
  output_path = normalizePath(cikti_yolu, winslash = "/", mustWork = TRUE)
)
