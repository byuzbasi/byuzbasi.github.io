# Bölüm 1, örnek 1: sentetik sıcaklık kayıtları.
# Üçüncü gün eksiktir; değer tahmin edilmez veya değiştirilmez.

sicaklik_c <- c(18.4, 19.1, NA_real_, 21.0)
olculdu <- !is.na(sicaklik_c)

ortalama_c <- mean(sicaklik_c, na.rm = TRUE)

message("Gözlem sayısı: ", length(sicaklik_c))
message("Ölçülen gün sayısı: ", sum(olculdu))
message(
  "Gözlenen sıcaklık ortalaması: ",
  format(ortalama_c, decimal.mark = ".", trim = TRUE),
  " C"
)
