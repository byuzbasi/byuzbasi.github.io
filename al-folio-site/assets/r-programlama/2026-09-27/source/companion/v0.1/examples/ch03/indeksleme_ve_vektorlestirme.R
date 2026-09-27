# Bölüm 3: indeksleme ve vektörleştirme.

puan <- c(Ayse = 78, Bora = 85, Ceren = NA_real_, Derya = 92, Efe = 74)

konumsal <- puan[c(1, 4)]
dislanan <- puan[-c(2, 3)]
mantiksal <- puan[!is.na(puan) & puan >= 80]
adli <- puan[c("Bora", "Efe")]

x <- c(1, 2, 3, 4)
y <- c(0.5, 1.0, 1.5, 2.0)
z <- x + y

tam_geri_donusum <- x + c(10, 20)
uyari_metni <- ""
kismi_geri_donusum <- withCallingHandlers(
  x + c(10, 20, 30),
  warning = function(w) {
    uyari_metni <<- conditionMessage(w)
    invokeRestart("muffleWarning")
  }
)

ozel <- c(sonlu = 1, eksik = NA_real_, tanimsiz = NaN,
          arti_sonsuz = Inf, eksi_sonsuz = -Inf)
ozel_durumlar <- data.frame(
  is_na = is.na(ozel),
  is_nan = is.nan(ozel),
  is_finite = is.finite(ozel),
  row.names = names(ozel)
)

stopifnot(
  identical(konumsal, c(Ayse = 78, Derya = 92)),
  identical(dislanan, c(Ayse = 78, Derya = 92, Efe = 74)),
  identical(mantiksal, c(Bora = 85, Derya = 92)),
  identical(adli, c(Bora = 85, Efe = 74)),
  identical(z, c(1.5, 3, 4.5, 6)),
  identical(tam_geri_donusum, c(11, 22, 13, 24)),
  length(kismi_geri_donusum) == 4L,
  nzchar(uyari_metni),
  identical(unname(ozel_durumlar$is_finite),
            c(TRUE, FALSE, FALSE, FALSE, FALSE))
)

cat("Konumsal seçim:", paste(konumsal, collapse = ", "), "\n")
cat("Mantıksal seçim:", paste(mantiksal, collapse = ", "), "\n")
cat("Vektörleştirilmiş toplam:", paste(z, collapse = ", "), "\n")
cat("Kısmi geri dönüşüm uyarısı yakalandı:", nzchar(uyari_metni), "\n")
print(ozel_durumlar)

ch03_result <- list(
  positional = konumsal,
  excluded = dislanan,
  logical = mantiksal,
  named = adli,
  vectorized_sum = z,
  exact_recycling = tam_geri_donusum,
  partial_recycling = kismi_geri_donusum,
  warning_text = uyari_metni,
  special_values = ozel_durumlar
)
