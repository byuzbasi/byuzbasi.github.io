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

required_packages <- c("R6", "rlang")
missing_packages <- required_packages[!vapply(
  required_packages,
  requireNamespace,
  quietly = TRUE,
  FUN.VALUE = logical(1)
)]
if (length(missing_packages)) {
  stop(
    "Bölüm 12 örneği için kurulu paketler gerekli: ",
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

new_runs_distribution_demo <- function(prob) {
  result <- runs_distribution_reference(prob)
  attr(result, "prob") <- validate_run_probabilities(prob)
  class(result) <- c("runs_distribution_demo", class(result))
  result
}

distribution_mean <- function(x, ...) {
  UseMethod("distribution_mean")
}

distribution_mean.runs_distribution_demo <- function(x, ...) {
  sum(x$runs * x$probability)
}

distribution_mean.default <- function(x, ...) {
  stop("Bu nesne için `distribution_mean()` yöntemi yok.", call. = FALSE)
}

prob <- c(0.20, 0.45, 0.70, 0.60)
s3_distribution <- new_runs_distribution_demo(prob)
s3_mean <- distribution_mean(s3_distribution)

s4_where <- environment()
invisible(methods::setPackageName(".GlobalEnv", s4_where))
if (!exists("new", envir = s4_where, inherits = TRUE)) {
  assign("new", methods::new, envir = s4_where)
}
RunsDistributionDemoV01 <- methods::setClass(
  "RunsDistributionDemoV01",
  slots = c(runs = "integer", probability = "numeric"),
  validity = function(object) {
    if (length(object@runs) == 0L ||
        length(object@runs) != length(object@probability)) {
      return("`runs` ve `probability` eşit ve pozitif uzunlukta olmalıdır.")
    }
    if (!identical(object@runs, seq_along(object@runs))) {
      return("`runs`, 1'den başlayan kesintisiz tamsayı desteği olmalıdır.")
    }
    if (any(!is.finite(object@probability)) ||
        any(object@probability < 0)) {
      return("`probability` sonlu ve negatif olmayan değerler taşımalıdır.")
    }
    if (abs(sum(object@probability) - 1) > 1e-12) {
      return("`probability` toplamı bir olmalıdır.")
    }
    TRUE
  },
  where = s4_where
)

invisible(methods::setGeneric(
  "pmf_total_demo",
  function(object) methods::standardGeneric("pmf_total_demo"),
  where = s4_where
))
methods::setMethod(
  "pmf_total_demo",
  signature = methods::signature(object = "RunsDistributionDemoV01"),
  function(object) sum(object@probability),
  where = s4_where
)

s4_distribution <- RunsDistributionDemoV01(
  runs = as.integer(s3_distribution$runs),
  probability = s3_distribution$probability
)
s4_total <- pmf_total_demo(s4_distribution)
s4_invalid <- tryCatch(
  RunsDistributionDemoV01(
    runs = 1:2,
    probability = c(0.40, 0.40)
  ),
  error = function(cnd) cnd
)

RunsAccumulatorDemo <- R6::R6Class(
  "RunsAccumulatorDemo",
  public = list(
    initialize = function() {
      private$mass <- 0
      private$batches <- 0L
    },
    add = function(x) {
      if (!inherits(x, "runs_distribution_demo")) {
        stop("`x` bir öğretim dağılımı olmalıdır.", call. = FALSE)
      }
      private$mass <- private$mass + sum(x$probability)
      private$batches <- private$batches + 1L
      invisible(self)
    },
    status = function() {
      list(mass = private$mass, batches = private$batches)
    }
  ),
  private = list(
    mass = NULL,
    batches = NULL
  ),
  lock_objects = TRUE
)

accumulator <- RunsAccumulatorDemo$new()
alias <- accumulator
accumulator$add(s3_distribution)
alias_status <- alias$status()
clone <- accumulator$clone(deep = TRUE)
clone$add(s3_distribution)
original_status <- accumulator$status()
clone_status <- clone$status()

probability <- -99
data_mask <- data.frame(
  probability = s3_distribution$probability,
  stringsAsFactors = FALSE
)
mean_expression <- quote(mean(probability))
base_mask_mean <- eval(mean_expression, envir = data_mask,
                       enclos = environment())
base_environment_mean <- mean(probability)

column_name <- "probability"
tidy_expression <- rlang::expr(mean(.data[[column_name]]))
tidy_mask_mean <- rlang::eval_tidy(
  tidy_expression,
  data = data_mask,
  env = environment()
)

capture_expression <- function(x) substitute(x)
captured_expression <- capture_expression(mean(probability))

stopifnot(
  inherits(s3_distribution, "runs_distribution_demo"),
  abs(s3_mean - runs_mean_reference(prob)) < 1e-12,
  abs(s4_total - 1) < 1e-12,
  inherits(s4_invalid, "error"),
  identical(alias_status$batches, 1L),
  abs(alias_status$mass - 1) < 1e-12,
  identical(original_status$batches, 1L),
  identical(clone_status$batches, 2L),
  abs(base_mask_mean - mean(data_mask$probability)) < 1e-12,
  identical(base_environment_mean, -99),
  abs(tidy_mask_mean - base_mask_mean) < 1e-12,
  identical(captured_expression, quote(mean(probability)))
)

cat("S3 sınıfı:", class(s3_distribution)[1L], "\n")
cat("S3 beklenen koşu sayısı:", sprintf("%.6f", s3_mean), "\n")
cat("S4 geçerlilik kapısı:", inherits(s4_invalid, "error"), "\n")
cat("R6 takma ad iş sayısı:", alias_status$batches, "\n")
cat("R6 özgün/kopya iş sayısı:",
    paste(c(original_status$batches, clone_status$batches), collapse = "/"),
    "\n")
cat("Veri maskesi/ortam ortalaması:",
    paste(sprintf("%.6f", c(base_mask_mean, base_environment_mean)),
          collapse = "/"),
    "\n")

ch12_result <- TRUE
