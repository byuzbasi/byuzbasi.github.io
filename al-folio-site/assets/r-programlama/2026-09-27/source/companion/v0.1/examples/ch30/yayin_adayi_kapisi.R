normalize_package_name <- function(x) {
  if (!is.character(x) || length(x) != 1L || is.na(x) || !nzchar(x)) {
    stop("Paket adı tek ve boş olmayan bir karakter dizisi olmalıdır.",
         call. = FALSE)
  }

  valid_shape <- nchar(x, type = "bytes") >= 2L &&
    grepl("^[A-Za-z][A-Za-z0-9.]*[A-Za-z0-9]$", x) &&
    !grepl("\\.\\.", x)
  if (!valid_shape) {
    stop("Paket adı bir harfle başlamalı; yalnız ASCII harf, rakam ve nokta içermelidir.",
         call. = FALSE)
  }

  tolower(x)
}

normalize_registry <- function(x) {
  if (!is.character(x)) {
    stop("Paket kayıtları karakter vektörü olmalıdır.", call. = FALSE)
  }
  x <- x[!is.na(x) & nzchar(x)]
  unique(tolower(x))
}

audit_package_name <- function(candidate,
                               current_cran = character(),
                               past_cran = character(),
                               current_bioconductor = character()) {
  normalized <- normalize_package_name(candidate)
  registries <- list(
    current_cran = normalize_registry(current_cran),
    past_cran = normalize_registry(past_cran),
    current_bioconductor = normalize_registry(current_bioconductor)
  )
  conflicts <- vapply(
    registries,
    function(registry) normalized %in% registry,
    logical(1)
  )

  list(
    candidate = candidate,
    normalized = normalized,
    clear = !any(conflicts),
    checks = data.frame(
      registry = names(conflicts),
      conflict = unname(conflicts),
      stringsAsFactors = FALSE
    )
  )
}

release_gate <- function(evidence) {
  required <- c(
    "identity_approved",
    "license_approved",
    "name_clear",
    "tests_passed",
    "source_archive_hashed",
    "r_release_check_passed",
    "r_devel_check_passed",
    "documentation_built",
    "secrets_absent"
  )
  if (!is.list(evidence) || is.null(names(evidence))) {
    stop("Kanıt, adlandırılmış bir liste olmalıdır.", call. = FALSE)
  }
  missing <- setdiff(required, names(evidence))
  if (length(missing)) {
    stop("Eksik yayın kapıları: ", paste(missing, collapse = ", "),
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

sglasso_case_snapshot <- function() {
  list(
    observed_on = "2026-09-07",
    github_research_package = list(
      package = "sglasso",
      version = "1.1.14",
      authors = "Bahadır Yüzbaşı ve Jiguo Cao",
      method = "Scaled Group Lasso",
      linking_to = c("Rcpp", "RcppArmadillo"),
      url = "https://github.com/byuzbasi/sglasso"
    ),
    existing_cran_package = list(
      package = "sglasso",
      version = "1.2.6",
      maintainer = "Luigi Augugliaro",
      method = "Structured graphical lasso for RCON(V,E) models",
      url = "https://CRAN.R-project.org/package=sglasso"
    )
  )
}

sglasso_snapshot <- sglasso_case_snapshot()
sglasso_name_audit <- audit_package_name(
  candidate = sglasso_snapshot$github_research_package$package,
  current_cran = sglasso_snapshot$existing_cran_package$package
)

blocked_release_example <- release_gate(list(
  identity_approved = TRUE,
  license_approved = TRUE,
  name_clear = sglasso_name_audit$clear,
  tests_passed = TRUE,
  source_archive_hashed = TRUE,
  r_release_check_passed = TRUE,
  r_devel_check_passed = TRUE,
  documentation_built = TRUE,
  secrets_absent = TRUE
))
