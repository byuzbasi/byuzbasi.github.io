# Bölüm 24: gerçek paket oluşturmadan R CMD araçlarını ve günlük ayrıştırmayı
# doğrulamak.

r_binary <- file.path(R.home("bin"), "R")
if (!file.exists(r_binary)) {
  stop("Etkin R çalıştırılabilir dosyası bulunamadı.", call. = FALSE)
}

probe_r_cmd_help <- function(subcommand) {
  output <- suppressWarnings(system2(
    r_binary,
    c("CMD", subcommand, "--help"),
    stdout = TRUE,
    stderr = TRUE
  ))
  status <- attr(output, "status")
  if (is.null(status)) {
    status <- 0L
  }
  list(
    subcommand = subcommand,
    status = as.integer(status),
    output = output,
    available = identical(as.integer(status), 0L) && length(output) > 0L
  )
}

command_probes <- lapply(c("build", "INSTALL", "check"), probe_r_cmd_help)
names(command_probes) <- c("build", "INSTALL", "check")

# Bu günlük sentetiktir. R CMD check çalıştırılmadı; amaç, önem düzeylerinin
# makinece sınıflandırılmasını küçük ve deterministik bir örnekle göstermektir.
synthetic_check_log <- c(
  "* checking R files for syntax errors ... ERROR",
  "* checking package dependencies ... WARNING",
  "* checking CRAN incoming feasibility ... NOTE",
  "* checking installed package size ... NOTE",
  "Status: 1 ERROR, 1 WARNING, 2 NOTEs"
)

diagnostic_counts <- c(
  ERROR = sum(grepl(" ERROR$", synthetic_check_log)),
  WARNING = sum(grepl(" WARNING$", synthetic_check_log)),
  NOTE = sum(grepl(" NOTE$", synthetic_check_log))
)
status_line <- grep("^Status:", synthetic_check_log, value = TRUE)

control_sequence <- data.frame(
  order = seq_len(5L),
  state = c(
    "source directory", "source archive", "temporary library",
    "installed package", "check directory"
  ),
  operation = c(
    "inspect", "R CMD build", "R CMD INSTALL",
    "load and examples", "R CMD check --as-cran"
  ),
  mutates_living_project = FALSE,
  performed_in_this_example = c(TRUE, FALSE, FALSE, FALSE, FALSE),
  stringsAsFactors = FALSE
)

platform_matrix <- data.frame(
  platform = c("Linux", "macOS", "Windows"),
  R_channel = c("release/devel", "release/devel", "release/devel"),
  required_gate = c(
    "source build, install, examples, tests",
    "source build, install, examples, tests",
    "source build, install, examples, tests"
  ),
  status = "not run; requires a real release candidate",
  stringsAsFactors = FALSE
)

ch24_result <- all(vapply(
  command_probes,
  function(probe) isTRUE(probe$available),
  FUN.VALUE = logical(1)
)) &&
  identical(unname(diagnostic_counts), c(1L, 1L, 2L)) &&
  length(status_line) == 1L &&
  all(!control_sequence$mutates_living_project) &&
  identical(
    control_sequence$performed_in_this_example,
    c(TRUE, FALSE, FALSE, FALSE, FALSE)
  ) &&
  nrow(platform_matrix) == 3L

if (!isTRUE(ch24_result)) {
  stop("Bölüm 24 komut veya tanı sınıflandırması başarısız.",
       call. = FALSE)
}

cat("Bölüm 24: R CMD yardım uçları ve sentetik günlük ayrıştırma geçti.\n")
