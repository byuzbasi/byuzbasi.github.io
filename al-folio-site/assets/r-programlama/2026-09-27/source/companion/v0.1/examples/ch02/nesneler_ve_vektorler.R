# Bölüm 2: nesneler, değerler ve atomik vektörler.

sicaklik_c <- c(
  pazartesi = 18.5,
  sali = 20.0,
  carsamba = NA_real_,
  persembe = 19.5
)

ornekler <- list(
  mantiksal = TRUE,
  tam_sayi = 4L,
  cift_duyarlikli = 4,
  karmasik = 2 + 3i,
  karakter = "R",
  ham = charToRaw("R")
)
turler <- vapply(ornekler, typeof, character(1))

karisik <- c(TRUE, 2L, 3.5)
karakter_karisimi <- c(FALSE, 2L, 2.5, "3")
etiketler <- c("10", "20", "30")
sayilar <- as.integer(etiketler)

ilk <- c(10, 20)
ikinci <- ilk
ikinci[1] <- 99

donusum_uyarisi <- ""
gecersiz_donusum <- withCallingHandlers(
  as.integer("on"),
  warning = function(w) {
    donusum_uyarisi <<- conditionMessage(w)
    invokeRestart("muffleWarning")
  }
)

bos_sayisal <- double()
olmayan <- NULL

stopifnot(
  identical(typeof(sicaklik_c), "double"),
  identical(names(sicaklik_c),
            c("pazartesi", "sali", "carsamba", "persembe")),
  identical(unname(turler),
            c("logical", "integer", "double", "complex", "character", "raw")),
  identical(typeof(karisik), "double"),
  identical(karakter_karisimi, c("FALSE", "2", "2.5", "3")),
  identical(sayilar, c(10L, 20L, 30L)),
  identical(ilk, c(10, 20)),
  identical(ikinci, c(99, 20)),
  is.na(gecersiz_donusum),
  nzchar(donusum_uyarisi),
  length(bos_sayisal) == 0L,
  typeof(bos_sayisal) == "double",
  length(olmayan) == 0L,
  is.null(olmayan)
)

cat("Sıcaklık vektörünün türü:", typeof(sicaklik_c), "\n")
cat("Sıcaklık vektörünün uzunluğu:", length(sicaklik_c), "\n")
cat("Atomik türler:\n")
print(turler, quote = FALSE)
cat("Karışık vektörün türü:", typeof(karisik), "\n")
cat("Açık dönüşüm sonucu:", paste(sayilar, collapse = ", "), "\n")

ch02_result <- list(
  temperatures = sicaklik_c,
  types = turler,
  coerced_vector = karisik,
  character_coercion = karakter_karisimi,
  explicit_conversion = sayilar,
  original_after_modified_binding = ilk,
  modified_binding = ikinci,
  invalid_conversion = gecersiz_donusum,
  conversion_warning = donusum_uyarisi,
  empty_numeric = bos_sayisal,
  absent_object = olmayan
)
