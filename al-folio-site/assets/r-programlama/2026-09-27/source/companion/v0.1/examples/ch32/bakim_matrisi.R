audit_api_change <- function(old_api, new_api, deprecations) {
  required <- c("name", "signature")
  if (!is.data.frame(old_api) || !all(required %in% names(old_api)) ||
      !is.data.frame(new_api) || !all(required %in% names(new_api))) {
    stop("Eski ve yeni API tablolarında name ve signature sütunları olmalıdır.",
         call. = FALSE)
  }
  if (anyDuplicated(old_api$name) || anyDuplicated(new_api$name)) {
    stop("API işlev adları benzersiz olmalıdır.", call. = FALSE)
  }
  if (!is.character(deprecations)) {
    stop("Kullanımdan kaldırma kaydı karakter vektörü olmalıdır.",
         call. = FALSE)
  }

  names_all <- union(old_api$name, new_api$name)
  old_index <- match(names_all, old_api$name)
  new_index <- match(names_all, new_api$name)
  old_signature <- old_api$signature[old_index]
  new_signature <- new_api$signature[new_index]
  change <- ifelse(
    is.na(old_index),
    "added",
    ifelse(
      is.na(new_index),
      "removed",
      ifelse(old_signature == new_signature, "unchanged", "signature_changed")
    )
  )
  notice_required <- change %in% c("removed", "signature_changed")
  notice_present <- !notice_required | names_all %in% deprecations

  table <- data.frame(
    name = names_all,
    old_signature = old_signature,
    new_signature = new_signature,
    change = change,
    notice_present = notice_present,
    stringsAsFactors = FALSE
  )
  list(
    compatible = all(notice_present),
    changes = table
  )
}

summarize_reverse_dependencies <- function(results) {
  required <- c("package", "status")
  if (!is.data.frame(results) || !all(required %in% names(results))) {
    stop("Ters bağımlılık tablosunda package ve status sütunları olmalıdır.",
         call. = FALSE)
  }
  allowed <- c("PASS", "FAIL", "SKIPPED")
  if (any(!results$status %in% allowed)) {
    stop("Bilinmeyen ters bağımlılık durumu var.", call. = FALSE)
  }

  counts <- table(factor(results$status, levels = allowed))
  list(
    total = nrow(results),
    passed = unname(as.integer(counts[["PASS"]])),
    failed = unname(as.integer(counts[["FAIL"]])),
    skipped = unname(as.integer(counts[["SKIPPED"]])),
    gate_passed = unname(counts[["FAIL"]]) == 0L &&
      unname(counts[["SKIPPED"]]) == 0L
  )
}

suggest_version_increment <- function(version, change) {
  if (!is.character(version) || length(version) != 1L ||
      !grepl("^[0-9]+\\.[0-9]+\\.[0-9]+$", version)) {
    stop("Sürüm x.y.z biçiminde olmalıdır.", call. = FALSE)
  }
  if (!change %in% c("patch", "minor", "major")) {
    stop("Değişiklik patch, minor veya major olmalıdır.", call. = FALSE)
  }
  parts <- as.integer(strsplit(version, ".", fixed = TRUE)[[1L]])
  if (change == "patch") {
    parts[[3L]] <- parts[[3L]] + 1L
  } else if (change == "minor") {
    parts[[2L]] <- parts[[2L]] + 1L
    parts[[3L]] <- 0L
  } else {
    parts[[1L]] <- parts[[1L]] + 1L
    parts[[2L]] <- 0L
    parts[[3L]] <- 0L
  }
  paste(parts, collapse = ".")
}

maintenance_gate <- function(evidence) {
  required <- c(
    "api_reviewed",
    "deprecations_documented",
    "reverse_dependencies_checked",
    "news_updated",
    "security_contact_current",
    "maintainer_contact_current",
    "checks_passed"
  )
  if (!is.list(evidence) || is.null(names(evidence))) {
    stop("Bakım kanıtı adlandırılmış bir liste olmalıdır.", call. = FALSE)
  }
  missing <- setdiff(required, names(evidence))
  if (length(missing)) {
    stop("Eksik bakım kapıları: ", paste(missing, collapse = ", "),
         call. = FALSE)
  }
  passed <- vapply(required, function(name) {
    value <- evidence[[name]]
    is.logical(value) && length(value) == 1L && !is.na(value) && value
  }, logical(1))

  list(
    passed = all(passed),
    checks = data.frame(
      gate = required,
      passed = unname(passed),
      stringsAsFactors = FALSE
    )
  )
}

old_api_example <- data.frame(
  name = c("fit_model", "predict_model"),
  signature = c("fit_model(x, y)", "predict_model(object, newdata)"),
  stringsAsFactors = FALSE
)
new_api_example <- data.frame(
  name = c("fit_model", "predict_model", "print_model"),
  signature = c(
    "fit_model(x, y)",
    "predict_model(object, newdata)",
    "print_model(object)"
  ),
  stringsAsFactors = FALSE
)
safe_api_audit <- audit_api_change(
  old_api_example,
  new_api_example,
  deprecations = character()
)
