# Bölüm 4: bileşik veri yapıları.

puan_matrisi <- matrix(
  1:6,
  nrow = 2,
  ncol = 3,
  dimnames = list(c("satir_1", "satir_2"), c("A", "B", "C"))
)

deney_dizisi <- array(
  seq_len(12),
  dim = c(gozlem = 2, degisken = 3, tekrar = 2)
)

grup <- factor(
  c("kontrol", "uygulama", "kontrol", "uygulama"),
  levels = c("kontrol", "uygulama")
)

ogrenciler <- data.frame(
  id = 1:4,
  ad = c("Ada", "Bora", "Ceren", "Deniz"),
  grup = grup,
  puan = c(78, NA_real_, 92, 85),
  stringsAsFactors = FALSE
)

calisma <- list(
  baslik = "Sentetik sınıf örneği",
  meta = list(kaynak = "sentetik", birim = "puan"),
  veri = ogrenciler,
  matris = puan_matrisi
)

tek_satir_vektor <- puan_matrisi[1, ]
tek_satir_matris <- puan_matrisi[1, , drop = FALSE]
baslik_listesi <- calisma["baslik"]
baslik_degeri <- calisma[["baslik"]]

sayisal_etiket <- factor(c("10", "20", "10"), levels = c("10", "20"))
duzey_kodlari <- as.integer(sayisal_etiket)
etiket_sayilari <- as.integer(as.character(sayisal_etiket))

stopifnot(
  identical(puan_matrisi[2, 3], (1:6)[2 + (3 - 1) * 2]),
  identical(dim(deney_dizisi), c(gozlem = 2L, degisken = 3L, tekrar = 2L)),
  is.factor(ogrenciler$grup),
  identical(unname(vapply(ogrenciler, length, integer(1))), rep(4L, 4)),
  is.null(dim(tek_satir_vektor)),
  identical(dim(tek_satir_matris), c(1L, 3L)),
  is.list(baslik_listesi),
  identical(baslik_degeri, "Sentetik sınıf örneği"),
  identical(duzey_kodlari, c(1L, 2L, 1L)),
  identical(etiket_sayilari, c(10L, 20L, 10L))
)

cat("Matris:\n")
print(puan_matrisi)
cat("Veri çerçevesi boyutu:", paste(dim(ogrenciler), collapse = " x "), "\n")
cat("drop = FALSE sonrası boyut:",
    paste(dim(tek_satir_matris), collapse = " x "), "\n")
cat("Faktör düzeyleri:", paste(levels(grup), collapse = ", "), "\n")

ch04_result <- list(
  matrix = puan_matrisi,
  array = deney_dizisi,
  data = ogrenciler,
  study = calisma,
  preserved_matrix = tek_satir_matris,
  factor_codes = duzey_kodlari,
  factor_labels_as_integer = etiket_sayilari
)
