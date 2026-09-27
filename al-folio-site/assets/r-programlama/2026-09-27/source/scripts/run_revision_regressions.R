#!/usr/bin/env Rscript
# Small regression checks for explanations corrected in the 2026-09-27 review.
script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
stopifnot(length(script_arg) == 1L)
project_dir <- normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), ".."))
paths <- c(list.files(file.path(project_dir, "companion"), "[.]R$",
                     recursive = TRUE, full.names = TRUE),
           list.files(file.path(project_dir, "scripts"), "[.]R$", full.names = TRUE))
for (path in paths) parse(path, encoding = "UTF-8")
stopifnot(is.na(unname(c(a = 1)["b"])), is.na(names(c(a = 1)["b"])))
stopifnot(isTRUE(withVisible(force(1))$visible))
if (getRversion() >= "4.3.0") {
  stopifnot(inherits(try(c(TRUE, FALSE) && TRUE, silent = TRUE), "try-error"))
  stopifnot(inherits(try(c(TRUE, FALSE) || FALSE, silent = TRUE), "try-error"))
}
i <- 0L
while (i < 3L) i <- i + 1L
j <- 0L
repeat {
  j <- j + 1L
  if (j >= 3L) break
}
stopifnot(i == 3L, j == 3L)
Sys.setenv(RBOOK_PROJECT_DIR = project_dir)
chapter7 <- new.env()
sys.source(file.path(project_dir, "companion/v0.1/examples/ch07/fonksiyon_tasarimi.R"),
           envir = chapter7)
message("Revision regressions: PASS; parsed ", length(paths), " R files.")
