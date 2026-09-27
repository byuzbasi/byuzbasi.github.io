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

required_packages <- c("dplyr", "tidyr")
missing_packages <- required_packages[!vapply(
  required_packages,
  requireNamespace,
  quietly = TRUE,
  FUN.VALUE = logical(1)
)]
if (length(missing_packages)) {
  stop(
    "Bölüm 13 örneği için kurulu paketler gerekli: ",
    paste(missing_packages, collapse = ", "),
    ". Otomatik kurulum yapılmadı.",
    call. = FALSE
  )
}

source(
  file.path(project_dir, "companion", "v0.1", "capstone-package",
            "prototype", "bernoulli_runs_reference.R"),
  local = TRUE,
  encoding = "UTF-8"
)

prob_scenarios <- list(
  alternating = c(0.15, 0.85, 0.20, 0.80),
  balanced = rep(0.50, 4L),
  early_shift = c(0.10, 0.20, 0.80, 0.90, 0.70)
)

build_exact_long <- function(prob_list) {
  pieces <- lapply(seq_along(prob_list), function(i) {
    distribution <- runs_distribution_reference(prob_list[[i]])
    data.frame(
      scenario_order = as.integer(i),
      scenario = names(prob_list)[[i]],
      n = as.integer(length(prob_list[[i]])),
      runs = as.integer(distribution$runs),
      probability = distribution$probability,
      cumulative = distribution$cumulative,
      stringsAsFactors = FALSE
    )
  })
  result <- do.call(rbind, pieces)
  row.names(result) <- NULL
  result
}

canonicalize_summary <- function(x) {
  x <- as.data.frame(x, stringsAsFactors = FALSE)
  x <- x[order(x$scenario), c("scenario", "probability", "percent")]
  row.names(x) <- NULL
  x
}

canonicalize_probability_long <- function(x) {
  x <- as.data.frame(x, stringsAsFactors = FALSE)
  x$runs <- as.integer(x$runs)
  x <- x[!is.na(x$probability), c("scenario", "runs", "probability")]
  x <- x[order(x$scenario, x$runs), ]
  row.names(x) <- NULL
  x
}

exact_long <- build_exact_long(prob_scenarios)
scenario_metadata <- data.frame(
  scenario = names(prob_scenarios),
  n = as.integer(lengths(prob_scenarios)),
  label = c("Dönüşümlü", "Dengeli", "Erken değişim"),
  stringsAsFactors = FALSE
)

# Base R: seçme, yeni sütun türetme ve gruplu toplama.
base_selected <- exact_long[c("scenario", "runs", "probability")]
base_derived <- transform(
  base_selected,
  percent = 100 * probability
)
base_summary <- stats::aggregate(
  cbind(probability, percent) ~ scenario,
  data = base_derived,
  FUN = sum
)

# tidyverse: aynı veri sözleşmesi, farklı fiiller.
tidy_summary <- exact_long |>
  dplyr::select(scenario, runs, probability) |>
  dplyr::mutate(percent = 100 * probability) |>
  dplyr::group_by(scenario) |>
  dplyr::summarise(
    probability = sum(probability),
    percent = sum(percent),
    .groups = "drop"
  )

# Base R birleştirmesi satır sırasını açık bir yardımcı anahtarla geri kurar.
base_join_input <- transform(exact_long, source_row = seq_len(nrow(exact_long)))
base_joined <- merge(
  base_join_input,
  scenario_metadata,
  by = c("scenario", "n"),
  all.x = TRUE,
  sort = FALSE
)
base_joined <- base_joined[order(base_joined$source_row), ]
row.names(base_joined) <- NULL

# dplyr birleştirmesi beklenen çoktan-bire ilişkiyi yürütme anında doğrular.
tidy_joined <- dplyr::left_join(
  exact_long,
  scenario_metadata,
  by = dplyr::join_by(scenario, n),
  relationship = "many-to-one",
  unmatched = "error"
)

# Geniş biçimde destek dışındaki koşu sayıları yapısal NA olarak görünür.
base_wide <- stats::reshape(
  exact_long[c("scenario", "runs", "probability")],
  idvar = "scenario",
  timevar = "runs",
  direction = "wide"
)
base_roundtrip <- stats::reshape(
  base_wide,
  varying = grep("^probability\\.", names(base_wide), value = TRUE),
  v.names = "probability",
  timevar = "runs",
  times = as.integer(sub("^probability\\.", "", grep(
    "^probability\\.", names(base_wide), value = TRUE
  ))),
  direction = "long"
)

tidy_wide <- exact_long |>
  dplyr::select(scenario, runs, probability) |>
  tidyr::pivot_wider(
    names_from = runs,
    values_from = probability,
    names_prefix = "run_"
  )
tidy_roundtrip <- tidy_wide |>
  tidyr::pivot_longer(
    cols = dplyr::starts_with("run_"),
    names_to = "runs",
    names_prefix = "run_",
    names_transform = list(runs = as.integer),
    values_to = "probability",
    values_drop_na = TRUE
  )

# Bilerek çoğaltılan bir sağ anahtar, beklenen çoktan-bire ilişkiyi bozar.
duplicated_metadata <- rbind(
  scenario_metadata,
  scenario_metadata[scenario_metadata$scenario == "balanced", ]
)
cardinality_error <- tryCatch(
  dplyr::left_join(
    exact_long,
    duplicated_metadata,
    by = dplyr::join_by(scenario, n),
    relationship = "many-to-one"
  ),
  error = function(cnd) cnd
)

base_missing_cells <- sum(is.na(base_wide))
tidy_missing_cells <- sum(is.na(tidy_wide))
base_join_view <- base_joined[
  c("scenario_order", "scenario", "n", "runs", "probability",
    "cumulative", "label")
]
tidy_join_view <- as.data.frame(tidy_joined, stringsAsFactors = FALSE)

stopifnot(
  identical(names(exact_long), c(
    "scenario_order", "scenario", "n", "runs", "probability", "cumulative"
  )),
  nrow(exact_long) == sum(lengths(prob_scenarios)),
  !anyDuplicated(exact_long[c("scenario", "runs")]),
  all(abs(stats::aggregate(probability ~ scenario, exact_long, sum)$probability -
            1) < 1e-12),
  isTRUE(all.equal(
    canonicalize_summary(base_summary),
    canonicalize_summary(tidy_summary),
    tolerance = 1e-14,
    check.attributes = FALSE
  )),
  identical(base_join_view, tidy_join_view),
  !anyNA(base_joined$label),
  identical(base_joined$source_row, seq_len(nrow(exact_long))),
  isTRUE(all.equal(
    canonicalize_probability_long(base_roundtrip),
    canonicalize_probability_long(exact_long),
    tolerance = 1e-14,
    check.attributes = FALSE
  )),
  isTRUE(all.equal(
    canonicalize_probability_long(tidy_roundtrip),
    canonicalize_probability_long(exact_long),
    tolerance = 1e-14,
    check.attributes = FALSE
  )),
  identical(base_missing_cells, 2L),
  identical(tidy_missing_cells, 2L),
  inherits(cardinality_error, "error")
)

cat("Uzun tablo satırı:", nrow(exact_long), "\n")
cat("Senaryo anahtarı benzersiz:", !anyDuplicated(scenario_metadata$scenario),
    "\n")
cat("Base/tidy özetleri eşdeğer: TRUE\n")
cat("Geniş biçimde yapısal NA:", tidy_missing_cells, "\n")
cat("Çoktan-bire ihlali reddedildi:", inherits(cardinality_error, "error"),
    "\n")

ch13_result <- TRUE
