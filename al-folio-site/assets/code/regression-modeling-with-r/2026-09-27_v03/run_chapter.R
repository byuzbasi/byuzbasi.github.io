#!/usr/bin/env Rscript
# Reproducible execution wrapper; chapter scripts remain plain, readable R.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3L || !args[2] %in% c("smoke", "complete")) {
  stop("Usage: Rscript --vanilla run_chapter.R CHAPTER smoke|complete NEW_OUTPUT_DIRECTORY")
}
chapter <- suppressWarnings(as.integer(args[1]))
if (is.na(chapter) || chapter < 1L || chapter > 12L) stop("Chapter must be 1-12.")
mode <- args[2]
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
if (length(script_arg) != 1L) stop("Run this wrapper with Rscript.")
package_dir <- dirname(normalizePath(sub("^--file=", "", script_arg)))
chapter_path <- file.path(package_dir, sprintf("ch%02d.R", chapter))
if (!file.exists(chapter_path)) stop("Missing chapter script: ", chapter_path)
required <- c("digest", if (chapter == 11L) "MASS",
              if (chapter == 12L) c("MASS", "glmnet", "knitr"))
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) stop("Missing packages: ", paste(missing, collapse = ", "))
output <- path.expand(args[3])
if (file.exists(output) || dir.exists(output)) stop("Refusing to overwrite: ", output)
if (!dir.create(output, recursive = TRUE)) stop("Cannot create output directory.")
output <- normalizePath(output)
code <- readLines(chapter_path, warn = FALSE, encoding = "UTF-8")
# Later blocks contain the tuning/stability workload. Smoke is explicitly a
# subset; it never changes seeds, data or the declared estimator.
if (mode == "smoke" && chapter %in% c(10L, 12L)) {
  cut <- grep("^# ===== Book block 3;", code)
  stopifnot(length(cut) == 1L)
  code <- code[seq_len(cut - 1L)]
}
writeLines(code, file.path(output, "executed_code.R"), useBytes = TRUE)
writeLines(c(paste("chapter", chapter), paste("mode", mode),
             paste("script_sha256", digest::digest(file = chapter_path, algo = "sha256")),
             paste("source_map_sha256", digest::digest(
               file = file.path(package_dir, "source_map.json"), algo = "sha256")),
             paste("started_utc", format(Sys.time(), tz = "UTC", usetz = TRUE)),
             paste("scope", if (mode == "smoke" && chapter %in% c(10L, 12L))
               "book blocks 1-2 only" else "all chapter book blocks")),
           file.path(output, "run_record.txt"))
writeLines(capture.output(sessionInfo()), file.path(output, "session_info.txt"))
old_directory <- setwd(output)
log <- file("console.txt", open = "wt", encoding = "UTF-8")
sink(log, split = TRUE)
sink(log, type = "message")
if (chapter %in% c(5L, 6L)) pdf("figures.pdf", width = 8, height = 6)
environment <- new.env(parent = globalenv())
failure <- tryCatch({
  source("executed_code.R", local = environment, echo = TRUE,
         print.eval = TRUE, max.deparse.length = Inf, encoding = "UTF-8")
  NULL
}, error = function(e) conditionMessage(e))
if (chapter %in% c(5L, 6L)) dev.off()
sink(type = "message")
sink()
close(log)
setwd(old_directory)
if (!is.null(failure)) {
  writeLines(failure, file.path(output, "FAILED.txt"))
  stop("Chapter failed; logs preserved at ", output, ": ", failure)
}
# Completion means execution, not statistical validity or future accuracy.
writeLines(c("Execution completed.", paste("mode", mode),
             "Check the separate review report for numerical validation and open issues."),
           file.path(output, "COMPLETED.txt"))
files <- list.files(output, full.names = TRUE)
manifest <- data.frame(
  file = basename(files), bytes = file.info(files)$size,
  sha256 = vapply(files, function(p) digest::digest(file = p, algo = "sha256"), character(1))
)
write.table(manifest, file.path(output, "manifest_sha256.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
cat("\n[PASS] Chapter execution completed; mode:", mode, "\nOutput:", output, "\n")
