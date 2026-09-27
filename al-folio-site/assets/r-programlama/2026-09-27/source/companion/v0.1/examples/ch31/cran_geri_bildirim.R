classify_cran_diagnostics <- function(lines) {
  if (!is.character(lines)) {
    stop("Kontrol günlüğü karakter vektörü olmalıdır.", call. = FALSE)
  }

  pattern <- "^\\* checking .+ \\.\\.\\. (ERROR|WARNING|NOTE)$"
  keep <- grepl(pattern, lines)
  selected <- lines[keep]
  severity <- sub(pattern, "\\1", selected)

  data.frame(
    diagnostic_id = sprintf("D%03d", seq_along(selected)),
    line_number = which(keep),
    severity = severity,
    message = selected,
    stringsAsFactors = FALSE
  )
}

evaluate_cran_responses <- function(diagnostics, responses) {
  required_diagnostics <- c("diagnostic_id", "severity", "message")
  required_responses <- c("diagnostic_id", "disposition", "action", "evidence")
  if (!is.data.frame(diagnostics) ||
      !all(required_diagnostics %in% names(diagnostics))) {
    stop("Tanı tablosunun gerekli sütunları yok.", call. = FALSE)
  }
  if (!is.data.frame(responses) ||
      !all(required_responses %in% names(responses))) {
    stop("Yanıt kaydının gerekli sütunları yok.", call. = FALSE)
  }
  if (anyDuplicated(responses$diagnostic_id)) {
    stop("Her tanı için en çok bir yanıt kaydı olmalıdır.", call. = FALSE)
  }

  index <- match(diagnostics$diagnostic_id, responses$diagnostic_id)
  disposition <- responses$disposition[index]
  action <- responses$action[index]
  evidence <- responses$evidence[index]
  allowed <- disposition %in% c("fixed", "explained")
  errors_or_warnings_explained <-
    diagnostics$severity %in% c("ERROR", "WARNING") &
    disposition != "fixed"
  complete_text <- !is.na(action) & nzchar(trimws(action)) &
    !is.na(evidence) & nzchar(trimws(evidence))
  resolved <- !is.na(index) & allowed & !errors_or_warnings_explained &
    complete_text

  register <- data.frame(
    diagnostics,
    disposition = disposition,
    action = action,
    evidence = evidence,
    resolved = resolved,
    stringsAsFactors = FALSE
  )
  list(
    ready_to_resubmit = nrow(register) > 0L && all(register$resolved),
    register = register
  )
}

validate_submission_sequence <- function(events, resubmission = FALSE) {
  if (!is.character(events) || anyNA(events) || any(!nzchar(events))) {
    stop("Gönderim olayları boş olmayan karakter değerleri olmalıdır.",
         call. = FALSE)
  }
  expected <- c(
    "source_frozen",
    "tarball_built",
    "tarball_checked",
    "form_submitted",
    "email_confirmed"
  )
  if (isTRUE(resubmission)) {
    expected <- c(
      expected,
      "feedback_received",
      "response_prepared",
      "version_increased",
      "resubmitted"
    )
  }

  list(
    valid = identical(events, expected),
    observed = events,
    expected = expected
  )
}

render_cran_comments <- function(package, version, check_matrix, notes) {
  if (!is.character(package) || length(package) != 1L || !nzchar(package) ||
      !is.character(version) || length(version) != 1L || !nzchar(version)) {
    stop("Paket ve sürüm tek, boş olmayan karakter değerleri olmalıdır.",
         call. = FALSE)
  }
  required <- c("platform", "r_version", "status")
  if (!is.data.frame(check_matrix) || !all(required %in% names(check_matrix))) {
    stop("Kontrol matrisinin gerekli sütunları yok.", call. = FALSE)
  }
  if (any(!check_matrix$status %in% c("OK", "NOTE", "WARNING", "ERROR"))) {
    stop("Bilinmeyen kontrol durumu var.", call. = FALSE)
  }
  if (!is.character(notes)) {
    stop("Notlar karakter vektörü olmalıdır.", call. = FALSE)
  }

  matrix_lines <- sprintf(
    "- %s, R %s: %s",
    check_matrix$platform,
    check_matrix$r_version,
    check_matrix$status
  )
  note_lines <- if (length(notes)) paste0("- ", notes) else "- None."
  c(
    sprintf("## R CMD check results for %s %s", package, version),
    "",
    matrix_lines,
    "",
    "## Downstream dependencies",
    "",
    "- None for a new package.",
    "",
    "## Comments",
    "",
    note_lines
  )
}

synthetic_check_log <- c(
  "* checking R files for syntax errors ... ERROR",
  "* checking whether package can be installed ... WARNING",
  "* checking CRAN incoming feasibility ... NOTE",
  "Status: 1 ERROR, 1 WARNING, 1 NOTE"
)
synthetic_diagnostics <- classify_cran_diagnostics(synthetic_check_log)
