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

required_packages <- c("jsonlite", "digest")
missing_packages <- required_packages[!vapply(
  required_packages,
  requireNamespace,
  quietly = TRUE,
  FUN.VALUE = logical(1)
)]
if (length(missing_packages)) {
  stop(
    "Bölüm 16 örneği için kurulu paketler gerekli: ",
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

simulation_spec <- list(
  schema_version = "1.0",
  pedagogical_scope = "small smoke test; not a production recommendation",
  prob = c(0.20, 0.45, 0.70, 0.60),
  replications = 64L,
  checkpoint_size = 16L,
  seed = 20260906L,
  rng_kind = "L'Ecuyer-CMRG",
  normal_kind = "Inversion",
  sample_kind = "Rejection",
  work_unit = "one Monte Carlo replication"
)
scientific_signature <- digest::digest(
  simulation_spec,
  algo = "sha256",
  serialize = TRUE
)

run_id <- Sys.getenv("RBOOK_CH16_RUN_ID", unset = "ch16-direct-v0.1")
if (!grepl("^[A-Za-z0-9._-]+$", run_id)) {
  stop("RBOOK_CH16_RUN_ID yalnızca güvenli ASCII karakterleri içerebilir.",
       call. = FALSE)
}

output_dir <- Sys.getenv("RBOOK_CH16_OUTPUT_DIR", unset = "")
if (!nzchar(output_dir)) {
  output_dir <- file.path(tempdir(), run_id)
}

stop_after_text <- Sys.getenv("RBOOK_CH16_STOP_AFTER_CHUNKS", unset = "4")
stop_after_chunks <- suppressWarnings(as.integer(stop_after_text))
total_chunks <- as.integer(
  simulation_spec$replications / simulation_spec$checkpoint_size
)
if (is.na(stop_after_chunks) || stop_after_chunks < 1L ||
    stop_after_chunks > total_chunks) {
  stop("RBOOK_CH16_STOP_AFTER_CHUNKS, 1 ile 4 arasında olmalıdır.",
       call. = FALSE)
}

atomic_write_json <- function(x, path) {
  temporary <- paste0(path, ".tmp")
  if (file.exists(temporary)) {
    stop("Artık geçici JSON dosyası bulundu: ", temporary, call. = FALSE)
  }
  jsonlite::write_json(
    x,
    temporary,
    pretty = TRUE,
    auto_unbox = TRUE,
    null = "null",
    na = "null"
  )
  if (!file.rename(temporary, path)) {
    stop("JSON dosyası atomik olarak yerine taşınamadı: ", path,
         call. = FALSE)
  }
  invisible(path)
}

atomic_save_rds <- function(x, path) {
  temporary <- paste0(path, ".tmp")
  if (file.exists(temporary)) {
    stop("Artık geçici RDS dosyası bulundu: ", temporary, call. = FALSE)
  }
  saveRDS(x, temporary, version = 3)
  if (!file.rename(temporary, path)) {
    stop("Checkpoint atomik olarak yerine taşınamadı: ", path,
         call. = FALSE)
  }
  invisible(path)
}

read_shard <- function(path, expected_ids, expected_signature) {
  shard <- tryCatch(
    readRDS(path),
    error = function(cnd) {
      stop("Checkpoint okunamadı: ", basename(path), "; ",
           conditionMessage(cnd), call. = FALSE)
    }
  )
  expected_names <- c(
    "replication", "chunk", "sequence", "runs", "scientific_signature"
  )
  valid <- is.data.frame(shard) && identical(names(shard), expected_names) &&
    identical(shard$replication, as.integer(expected_ids)) &&
    nrow(shard) == length(expected_ids) &&
    !anyDuplicated(shard$replication) &&
    all(shard$chunk == as.integer(ceiling(expected_ids /
                                           simulation_spec$checkpoint_size))) &&
    all(nchar(shard$sequence) == length(simulation_spec$prob)) &&
    all(grepl("^[01]+$", shard$sequence)) &&
    all(shard$runs >= 1L & shard$runs <= length(simulation_spec$prob)) &&
    all(shard$scientific_signature == expected_signature)
  if (!isTRUE(valid)) {
    stop(
      "Geçersiz veya bilimsel imzası uyuşmayan checkpoint reddedildi: ",
      basename(path),
      call. = FALSE
    )
  }
  shard
}

chunk_ids <- function(chunk) {
  first <- (chunk - 1L) * simulation_spec$checkpoint_size + 1L
  last <- chunk * simulation_spec$checkpoint_size
  seq.int(first, last)
}

chunk_path <- function(chunk) {
  file.path(output_dir, "checkpoints", sprintf("chunk_%03d.rds", chunk))
}

make_replication_streams <- function() {
  RNGkind(
    kind = simulation_spec$rng_kind,
    normal.kind = simulation_spec$normal_kind,
    sample.kind = simulation_spec$sample_kind
  )
  set.seed(simulation_spec$seed)
  state <- get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  streams <- vector("list", simulation_spec$replications)
  for (i in seq_len(simulation_spec$replications)) {
    streams[[i]] <- state
    state <- parallel::nextRNGStream(state)
  }
  streams
}

simulate_replication <- function(replication, state) {
  assign(".Random.seed", state, envir = .GlobalEnv)
  sequence <- as.integer(
    stats::runif(length(simulation_spec$prob)) < simulation_spec$prob
  )
  data.frame(
    replication = as.integer(replication),
    chunk = as.integer(ceiling(replication /
                                 simulation_spec$checkpoint_size)),
    sequence = paste0(sequence, collapse = ""),
    runs = count_runs_reference(sequence),
    scientific_signature = scientific_signature,
    stringsAsFactors = FALSE
  )
}

write_progress <- function(status, completed_ids, session_completed,
                           started_at, last_work_unit = NA_integer_) {
  now <- Sys.time()
  elapsed <- max(as.numeric(difftime(now, started_at, units = "secs")),
                 1e-6)
  completed <- length(completed_ids)
  pending <- simulation_spec$replications - completed
  throughput <- if (session_completed > 0L) session_completed / elapsed else NA_real_
  eta_seconds <- if (is.finite(throughput) && throughput > 0 && pending > 0L) {
    pending / throughput
  } else if (pending == 0L) {
    0
  } else {
    NA_real_
  }
  snapshot <- list(
    schema_version = "1.0",
    run_id = run_id,
    scientific_signature = scientific_signature,
    status = status,
    phase = if (pending == 0L) "validation_complete" else "simulation",
    work_unit = simulation_spec$work_unit,
    total = simulation_spec$replications,
    validated_completed = completed,
    running = 0L,
    failed = 0L,
    pending = pending,
    percent_complete = 100 * completed / simulation_spec$replications,
    elapsed_seconds_this_session = elapsed,
    throughput_per_second_this_session = if (is.finite(throughput)) {
      throughput
    } else {
      NULL
    },
    estimated_remaining_seconds = if (is.finite(eta_seconds)) {
      eta_seconds
    } else {
      NULL
    },
    eta_status = if (is.finite(eta_seconds)) "estimated" else "estimating",
    last_heartbeat_utc = format(now, tz = "UTC", usetz = TRUE),
    last_completed_work_unit = if (is.na(last_work_unit)) NULL else last_work_unit
  )
  atomic_write_json(snapshot, file.path(output_dir, "progress.json"))

  progress_row <- data.frame(
    timestamp_utc = snapshot$last_heartbeat_utc,
    status = status,
    phase = snapshot$phase,
    total = snapshot$total,
    completed = completed,
    running = 0L,
    failed = 0L,
    pending = pending,
    percent_complete = snapshot$percent_complete,
    elapsed_seconds_this_session = elapsed,
    throughput_per_second_this_session = if (is.finite(throughput)) {
      throughput
    } else {
      NA_real_
    },
    estimated_remaining_seconds = if (is.finite(eta_seconds)) {
      eta_seconds
    } else {
      NA_real_
    },
    last_completed_work_unit = last_work_unit,
    stringsAsFactors = FALSE
  )
  history_path <- file.path(output_dir, "progress.tsv")
  utils::write.table(
    progress_row,
    history_path,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE,
    col.names = !file.exists(history_path),
    append = file.exists(history_path),
    na = ""
  )
  invisible(snapshot)
}

run_ch16_pipeline <- function() {
  old_kind <- RNGkind()
  old_seed_exists <- exists(".Random.seed", envir = .GlobalEnv,
                            inherits = FALSE)
  old_seed <- if (old_seed_exists) {
    get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  } else {
    NULL
  }
  on.exit({
    do.call(RNGkind, as.list(old_kind))
    if (old_seed_exists) {
      assign(".Random.seed", old_seed, envir = .GlobalEnv)
    } else if (exists(".Random.seed", envir = .GlobalEnv,
                      inherits = FALSE)) {
      rm(".Random.seed", envir = .GlobalEnv)
    }
  }, add = TRUE)

  metadata_path <- file.path(output_dir, "run_metadata.json")
  if (!file.exists(output_dir)) {
    dir.create(file.path(output_dir, "checkpoints"), recursive = TRUE,
               showWarnings = FALSE)
    atomic_write_json(
      list(
        schema_version = "1.0",
        run_id = run_id,
        created_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
        scientific_signature = scientific_signature,
        specification = simulation_spec
      ),
      metadata_path
    )
  } else {
    if (!dir.exists(output_dir) || !file.exists(metadata_path) ||
        !dir.exists(file.path(output_dir, "checkpoints"))) {
      stop(
        "Mevcut çıktı dizini geçerli bir Bölüm 16 çalışması değil; üzerine yazılmadı.",
        call. = FALSE
      )
    }
    metadata <- jsonlite::read_json(metadata_path, simplifyVector = TRUE)
    if (!identical(metadata$scientific_signature, scientific_signature) ||
        !identical(metadata$run_id, run_id)) {
      stop("Çalışma kimliği veya bilimsel imza uyuşmuyor; devam reddedildi.",
           call. = FALSE)
    }
  }

  started_at <- Sys.time()
  streams <- make_replication_streams()
  valid_shards <- list()
  for (chunk in seq_len(total_chunks)) {
    path <- chunk_path(chunk)
    if (file.exists(path)) {
      valid_shards[[as.character(chunk)]] <- read_shard(
        path,
        chunk_ids(chunk),
        scientific_signature
      )
    }
  }
  completed_ids <- if (length(valid_shards)) {
    sort(as.integer(unlist(lapply(valid_shards, `[[`, "replication"))))
  } else {
    integer()
  }
  write_progress(
    "RUNNING",
    completed_ids,
    session_completed = 0L,
    started_at = started_at,
    last_work_unit = if (length(completed_ids)) max(completed_ids) else NA_integer_
  )

  session_completed <- 0L
  for (chunk in seq_len(stop_after_chunks)) {
    path <- chunk_path(chunk)
    ids <- chunk_ids(chunk)
    if (file.exists(path)) {
      valid_shards[[as.character(chunk)]] <- read_shard(
        path, ids, scientific_signature
      )
      next
    }
    rows <- lapply(ids, function(replication) {
      simulate_replication(replication, streams[[replication]])
    })
    shard <- do.call(rbind, rows)
    row.names(shard) <- NULL
    atomic_save_rds(shard, path)
    valid_shards[[as.character(chunk)]] <- read_shard(
      path, ids, scientific_signature
    )
    session_completed <- session_completed + length(ids)
    completed_ids <- sort(as.integer(unlist(lapply(
      valid_shards, `[[`, "replication"
    ))))
    write_progress(
      "RUNNING",
      completed_ids,
      session_completed,
      started_at,
      last_work_unit = max(ids)
    )
  }

  completed_ids <- sort(as.integer(unlist(lapply(
    valid_shards, `[[`, "replication"
  ))))
  complete <- identical(completed_ids, seq_len(simulation_spec$replications))
  if (!complete) {
    progress <- write_progress(
      "PAUSED_FOR_RESUME",
      completed_ids,
      session_completed,
      started_at,
      last_work_unit = if (length(completed_ids)) max(completed_ids) else NA_integer_
    )
    return(list(
      passed = TRUE,
      complete = FALSE,
      completed = length(completed_ids),
      resumed_valid_work_units = length(completed_ids) - session_completed,
      scientific_signature = scientific_signature,
      progress = progress,
      output_dir = output_dir
    ))
  }

  records <- do.call(rbind, valid_shards[as.character(seq_len(total_chunks))])
  records <- records[order(records$replication), ]
  row.names(records) <- NULL
  support <- seq_along(simulation_spec$prob)
  estimated_probability <- as.numeric(
    table(factor(records$runs, levels = support)) /
      simulation_spec$replications
  )
  exact_distribution <- runs_distribution_reference(simulation_spec$prob)
  summary <- data.frame(
    runs = as.integer(support),
    exact_probability = exact_distribution$probability,
    estimated_probability = estimated_probability,
    monte_carlo_standard_error = sqrt(
      estimated_probability * (1 - estimated_probability) /
        simulation_spec$replications
    ),
    replications = simulation_spec$replications,
    stringsAsFactors = FALSE
  )

  records_path <- file.path(output_dir, "simulation_records.tsv")
  summary_path <- file.path(output_dir, "simulation_summary.tsv")
  completion_path <- file.path(output_dir, "completion.json")
  if (any(file.exists(c(records_path, summary_path, completion_path)))) {
    stop(
      "Nihai simülasyon çıktısı zaten var; sessizce üzerine yazılmadı.",
      call. = FALSE
    )
  }
  utils::write.table(
    records,
    records_path,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE
  )
  utils::write.table(
    summary,
    summary_path,
    sep = "\t",
    quote = FALSE,
    row.names = FALSE
  )
  atomic_write_json(
    list(
      schema_version = "1.0",
      run_id = run_id,
      scientific_signature = scientific_signature,
      status = "COMPLETE",
      validated_work_units = nrow(records),
      total_work_units = simulation_spec$replications,
      completed_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE)
    ),
    completion_path
  )

  stopifnot(
    identical(records$replication, seq_len(simulation_spec$replications)),
    !anyDuplicated(records$replication),
    all(records$scientific_signature == scientific_signature),
    nrow(summary) == length(simulation_spec$prob),
    abs(sum(summary$estimated_probability) - 1) < 1e-15,
    all(summary$monte_carlo_standard_error >= 0),
    isTRUE(all.equal(
      summary$monte_carlo_standard_error,
      sqrt(summary$estimated_probability *
             (1 - summary$estimated_probability) /
             simulation_spec$replications),
      tolerance = 0
    ))
  )

  progress <- write_progress(
    "COMPLETE",
    completed_ids,
    session_completed,
    started_at,
    last_work_unit = max(completed_ids)
  )
  list(
    passed = TRUE,
    complete = TRUE,
    completed = nrow(records),
    resumed_valid_work_units = nrow(records) - session_completed,
    scientific_signature = scientific_signature,
    records = records,
    summary = summary,
    summary_path = summary_path,
    progress = progress,
    output_dir = output_dir
  )
}

ch16_pipeline <- run_ch16_pipeline()
ch16_result <- isTRUE(ch16_pipeline$passed)

cat("Bilimsel imza:", scientific_signature, "\n")
cat("Geçerli iş birimi:", ch16_pipeline$completed, "/",
    simulation_spec$replications, "\n")
cat("Çalışma durumu:", if (ch16_pipeline$complete) "COMPLETE" else "PAUSED",
    "\n")
if (ch16_pipeline$complete) {
  cat("Monte Carlo standart hatası formülü doğrulandı: TRUE\n")
}
