args_full <- commandArgs(trailingOnly = FALSE)
project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  file_arg <- grep("^--file=", args_full, value = TRUE)
  if (length(file_arg) != 1L) stop("Betik yolu belirlenemedi.", call. = FALSE)
  script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
  project_dir <- normalizePath(
    file.path(dirname(script_path), "..", "..", "..", ".."),
    mustWork = TRUE
  )
}

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  stop(
    "Bölüm 14 örneği kurulu `ggplot2` paketini gerektirir; otomatik kurulum yapılmadı.",
    call. = FALSE
  )
}

source(
  file.path(project_dir, "companion", "v0.1", "capstone-package",
            "prototype", "bernoulli_runs_reference.R"),
  local = TRUE,
  encoding = "UTF-8"
)

output_dir <- Sys.getenv("RBOOK_CH14_OUTPUT_DIR", unset = "")
if (!nzchar(output_dir)) {
  output_dir <- file.path(tempdir(), "rbook-ch14-figures-v0.1")
}
if (dir.exists(output_dir) && length(list.files(output_dir, all.files = TRUE,
                                                no.. = TRUE))) {
  stop("Bölüm 14 çıktı dizini boş değil; üzerine yazılmadı: ", output_dir,
       call. = FALSE)
}
if (file.exists(output_dir) && !dir.exists(output_dir)) {
  stop("Bölüm 14 çıktı yolu bir dizin değil: ", output_dir, call. = FALSE)
}
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

prob <- c(0.20, 0.45, 0.70, 0.60)
distribution <- runs_distribution_reference(prob)
plot_data <- rbind(
  data.frame(
    runs = distribution$runs,
    measure = "Olasılık kütlesi",
    value = distribution$probability,
    stringsAsFactors = FALSE
  ),
  data.frame(
    runs = distribution$runs,
    measure = "Birikimli olasılık",
    value = distribution$cumulative,
    stringsAsFactors = FALSE
  )
)
plot_data$measure <- factor(
  plot_data$measure,
  levels = c("Olasılık kütlesi", "Birikimli olasılık")
)

palette <- c(
  "Olasılık kütlesi" = "#183848",
  "Birikimli olasılık" = "#A14C32"
)
line_types <- c("Olasılık kütlesi" = 1, "Birikimli olasılık" = 2)
point_shapes <- c("Olasılık kütlesi" = 16, "Birikimli olasılık" = 17)

base_pdf <- file.path(output_dir, "kosu_dagilimi_base_v0_1_rev02.pdf")
ggplot_pdf <- file.path(output_dir, "kosu_dagilimi_ggplot2_v0_1_rev02.pdf")
data_tsv <- file.path(
  output_dir, "kosu_dagilimi_cizim_verisi_v0_1_rev02.tsv"
)
output_paths <- c(base_pdf, ggplot_pdf, data_tsv)
if (any(file.exists(output_paths))) {
  stop("Bölüm 14 çıktılarından en az biri zaten var; üzerine yazılmadı.",
       call. = FALSE)
}

wide_values <- cbind(
  "Olasılık kütlesi" = distribution$probability,
  "Birikimli olasılık" = distribution$cumulative
)
grDevices::cairo_pdf(base_pdf, width = 6.5, height = 4.2, family = "sans")
graphics::par(mar = c(6.2, 4.2, 4.2, 1.2) + 0.1)
graphics::matplot(
  distribution$runs,
  wide_values,
  type = "o",
  lty = unname(line_types),
  pch = unname(point_shapes),
  col = unname(palette),
  lwd = 2,
  xlab = "Toplam koşu sayısı",
  ylab = "Olasılık",
  ylim = c(0, 1),
  xaxt = "n",
  main = "Kesin koşu sayısı dağılımı"
)
graphics::axis(1, at = distribution$runs)
graphics::grid(nx = NA, ny = NULL, col = "#D7DEE1", lty = 1)
graphics::matlines(
  distribution$runs,
  wide_values,
  type = "o",
  lty = unname(line_types),
  pch = unname(point_shapes),
  col = unname(palette),
  lwd = 2
)
graphics::legend(
  "topleft",
  legend = colnames(wide_values),
  col = unname(palette),
  lty = unname(line_types),
  pch = unname(point_shapes),
  lwd = 2,
  bty = "n",
  cex = 0.85
)
graphics::mtext(
  "Girdi: prob = (0.20, 0.45, 0.70, 0.60); kesin saf-R başvurusu",
  side = 1,
  line = 4.5,
  cex = 0.72,
  col = "#52666F"
)
grDevices::dev.off()

ggplot_object <- ggplot2::ggplot(
  plot_data,
  ggplot2::aes(
    x = runs,
    y = value,
    colour = measure,
    linetype = measure,
    shape = measure,
    group = measure
  )
) +
  ggplot2::geom_line(linewidth = 0.9) +
  ggplot2::geom_point(size = 2.5) +
  ggplot2::scale_x_continuous(breaks = distribution$runs) +
  ggplot2::scale_y_continuous(
    limits = c(0, 1),
    breaks = seq(0, 1, by = 0.2),
    expand = ggplot2::expansion(mult = c(0, 0.02))
  ) +
  ggplot2::scale_colour_manual(values = palette) +
  ggplot2::scale_linetype_manual(values = line_types) +
  ggplot2::scale_shape_manual(values = point_shapes) +
  ggplot2::labs(
    title = "Kesin koşu sayısı dağılımı",
    subtitle = "prob = (0.20, 0.45, 0.70, 0.60)",
    x = "Toplam koşu sayısı",
    y = "Olasılık",
    colour = NULL,
    linetype = NULL,
    shape = NULL,
    caption = "Kaynak: kitapla birlikte sınanan saf-R başvuru prototipi"
  ) +
  ggplot2::theme_minimal(base_size = 11) +
  ggplot2::theme(
    legend.position = "top",
    panel.grid.minor = ggplot2::element_blank(),
    plot.title = ggplot2::element_text(face = "bold", colour = "#183848"),
    plot.caption = ggplot2::element_text(colour = "#52666F")
  )
ggplot2::ggsave(
  filename = ggplot_pdf,
  plot = ggplot_object,
  device = grDevices::cairo_pdf,
  width = 6.5,
  height = 4.2,
  units = "in"
)

utils::write.table(
  transform(plot_data, measure = as.character(measure)),
  data_tsv,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

stopifnot(
  nrow(plot_data) == 2L * nrow(distribution),
  !anyDuplicated(plot_data[c("runs", "measure")]),
  identical(range(plot_data$runs), c(1L, length(prob))),
  all(is.finite(plot_data$value)),
  all(plot_data$value >= 0 & plot_data$value <= 1),
  abs(sum(distribution$probability) - 1) < 1e-12,
  all(file.exists(output_paths)),
  all(file.info(c(base_pdf, ggplot_pdf))$size > 500L),
  file.info(data_tsv)$size > 0L
)

cat("Çizim verisi satırı:", nrow(plot_data), "\n")
cat("Base vektör PDF:", basename(base_pdf), "\n")
cat("ggplot2 vektör PDF:", basename(ggplot_pdf), "\n")
cat("Renk dışı kodlama: çizgi türü ve nokta şekli\n")

ch14_result <- TRUE
