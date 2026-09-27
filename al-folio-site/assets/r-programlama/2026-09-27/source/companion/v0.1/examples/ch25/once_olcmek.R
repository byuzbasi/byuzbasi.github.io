# Bölüm 25: performans iddiası kurmadan önce ölçüm protokolü.

validate_measurement_count <- function(value, name) {
  if (!is.numeric(value) || length(value) != 1L || is.na(value) ||
      !is.finite(value) || value < 1 || value != as.integer(value)) {
    stop("`", name, "` pozitif bir tamsayı olmalıdır.", call. = FALSE)
  }
  as.integer(value)
}

decompose_native_cost <- function(setup, transfer, compute, return_cost) {
  components <- c(
    setup = setup,
    transfer = transfer,
    compute = compute,
    return = return_cost
  )
  if (!is.numeric(components) || anyNA(components) ||
      any(!is.finite(components)) || any(components < 0)) {
    stop("Maliyet bileşenleri sonlu ve negatif olmayan sayılar olmalıdır.",
         call. = FALSE)
  }
  c(components, total = sum(components))
}

compute_speedup <- function(reference_time, candidate_time) {
  values <- c(reference_time = reference_time, candidate_time = candidate_time)
  if (anyNA(values) || any(!is.finite(values)) || any(values <= 0)) {
    stop("Süreler sonlu ve kesinlikle pozitif olmalıdır.", call. = FALSE)
  }
  unname(reference_time / candidate_time)
}

measure_runs_reference <- function(prob, repetitions = 5L) {
  repetitions <- validate_measurement_count(repetitions, "repetitions")
  expected <- runs_pmf_reference(prob)

  # İlk çağrı derleme değil; işlev ve veri yollarının ısınmasını ayrı tutar.
  invisible(runs_pmf_reference(prob))
  elapsed <- numeric(repetitions)
  outputs_identical <- logical(repetitions)

  for (iteration in seq_len(repetitions)) {
    measured <- system.time({
      observed <- runs_pmf_reference(prob)
    })
    elapsed[iteration] <- unname(measured[["elapsed"]])
    outputs_identical[iteration] <- identical(observed, expected)
  }

  data.frame(
    repetition = seq_len(repetitions),
    elapsed_seconds = elapsed,
    output_identical = outputs_identical,
    stringsAsFactors = FALSE
  )
}

profile_runs_reference <- function(prob, calls = 25L, profile_path) {
  calls <- validate_measurement_count(calls, "calls")
  if (!is.character(profile_path) || length(profile_path) != 1L ||
      !nzchar(profile_path)) {
    stop("`profile_path` tek ve boş olmayan bir dosya yolu olmalıdır.",
         call. = FALSE)
  }
  if (file.exists(profile_path)) {
    stop("Profil dosyası zaten var; üzerine yazılmadı.", call. = FALSE)
  }

  expected <- runs_pmf_reference(prob)
  profiling_active <- FALSE
  on.exit({
    if (profiling_active) utils::Rprof(NULL)
  }, add = TRUE)

  utils::Rprof(profile_path, interval = 0.001)
  profiling_active <- TRUE
  for (iteration in seq_len(calls)) {
    observed <- runs_pmf_reference(prob)
    if (!identical(observed, expected)) {
      stop("Profilleme sırasında referans çıktı değişti.", call. = FALSE)
    }
  }
  utils::Rprof(NULL)
  profiling_active <- FALSE

  summary <- utils::summaryRprof(profile_path)
  by_total <- summary$by.total
  if (is.null(by_total) || !nrow(by_total)) {
    by_total <- data.frame(
      total.time = numeric(),
      total.pct = numeric(),
      self.time = numeric(),
      self.pct = numeric(),
      check.names = FALSE
    )
  }

  list(
    calls = calls,
    output = expected,
    sample_interval_seconds = 0.001,
    sampled_functions = by_total,
    profile_path = normalizePath(profile_path, mustWork = TRUE)
  )
}
