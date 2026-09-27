# Bölüm 18: paket-nötr API sözleşmesi denetimi.
#
# Bu dosyadaki adlar yayımlanmış API değildir. Yaşayan paket adı ve lisansı
# kararlaştırılıncaya kadar mevcut saf-R prototipi değiştirilmeden kullanılır.

project_dir <- Sys.getenv("RBOOK_PROJECT_DIR", unset = "")
if (!nzchar(project_dir)) {
  stop("RBOOK_PROJECT_DIR zorunludur.", call. = FALSE)
}
project_dir <- normalizePath(project_dir, mustWork = TRUE)

prototype_path <- file.path(
  project_dir, "companion", "v0.1", "capstone-package", "prototype",
  "bernoulli_runs_reference.R"
)
if (!file.exists(prototype_path)) {
  stop("Saf-R bilimsel referans prototipi bulunamadı.", call. = FALSE)
}

prototype_environment <- new.env(parent = baseenv())
sys.source(prototype_path, envir = prototype_environment, keep.source = TRUE)

required_functions <- c(
  "validate_run_probabilities", "runs_distribution_reference",
  "runs_tail_reference"
)
if (!all(vapply(
  required_functions,
  exists,
  envir = prototype_environment,
  inherits = FALSE,
  FUN.VALUE = logical(1)
))) {
  stop("Saf-R prototipinin gereken işlevleri eksik.", call. = FALSE)
}

validate_run_probabilities <- get(
  "validate_run_probabilities", envir = prototype_environment,
  inherits = FALSE
)
runs_distribution_reference <- get(
  "runs_distribution_reference", envir = prototype_environment,
  inherits = FALSE
)
runs_tail_reference <- get(
  "runs_tail_reference", envir = prototype_environment,
  inherits = FALSE
)

# Yalnız öğretim amacıyla kurulan aday sarmalayıcı. Bu işlev yaşayan paketin
# kesin adı, dışa açılan işlevi veya geriye uyumluluk vaadi değildir.
distribution_api_candidate <- function(prob) {
  validated <- validate_run_probabilities(prob)
  result <- runs_distribution_reference(validated)
  expected_names <- c("runs", "probability", "cumulative")
  if (!identical(names(result), expected_names)) {
    stop("Bilimsel çekirdeğin çıktı şeması beklenenden farklı.", call. = FALSE)
  }
  result
}

capture_error <- function(expr) {
  tryCatch(
    {
      force(expr)
      NULL
    },
    error = function(cnd) cnd
  )
}

prob <- c(0.10, 0.45, 0.80, 0.35)
prob_before <- prob
working_directory_before <- getwd()
options_before <- options()
seed_existed_before <- exists(
  ".Random.seed", envir = .GlobalEnv, inherits = FALSE
)
seed_before <- if (seed_existed_before) {
  get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
} else {
  NULL
}

distribution <- distribution_api_candidate(prob)
tail_result <- runs_tail_reference(
  x = c(0L, 1L, 1L, 0L),
  prob = prob,
  tail = "upper"
)
input_error <- capture_error(distribution_api_candidate(c(0.2, NA_real_)))

seed_existed_after <- exists(
  ".Random.seed", envir = .GlobalEnv, inherits = FALSE
)
seed_after <- if (seed_existed_after) {
  get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
} else {
  NULL
}

api_contract <- data.frame(
  responsibility = c(
    "validation", "scientific computation", "presentation", "error reporting"
  ),
  owner = c(
    "input validator", "unchanged reference core", "caller or documentation",
    "classed condition"
  ),
  evidence = c(
    "finite probabilities in [0, 1]",
    "runs, probability, cumulative",
    "raw data frame; no printing side effect",
    "runs_input_error with argument field"
  ),
  stringsAsFactors = FALSE
)

compatibility_baseline <- list(
  candidate_formals = names(formals(distribution_api_candidate)),
  result_class = class(distribution),
  result_names = names(distribution),
  tail_class = class(tail_result),
  error_class = class(input_error)
)

rng_unchanged <- identical(seed_existed_before, seed_existed_after) &&
  (!seed_existed_before || identical(seed_before, seed_after))

ch18_result <- identical(prob, prob_before) &&
  identical(getwd(), working_directory_before) &&
  identical(options(), options_before) &&
  rng_unchanged &&
  identical(names(distribution), c("runs", "probability", "cumulative")) &&
  isTRUE(all.equal(sum(distribution$probability), 1, tolerance = 1e-12)) &&
  inherits(input_error, "runs_input_error") &&
  identical(input_error$argument, "prob") &&
  identical(compatibility_baseline$candidate_formals, "prob")

if (!isTRUE(ch18_result)) {
  stop("Bölüm 18 API sözleşmesi denetimi başarısız.", call. = FALSE)
}

cat("Bölüm 18: API sorumlulukları, sınıflı hata ve yan etkisizlik geçti.\n")
