args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1L) normalizePath(args[[1]], mustWork = TRUE) else getwd()
lab_dir <- file.path(root, "labs", "r")
files <- sort(list.files(lab_dir, pattern = "\\.qmd$", full.names = TRUE))

extract_r_chunks <- function(lines) {
  chunks <- list()
  current <- character()
  in_chunk <- FALSE
  fence <- NULL
  for (line in lines) {
    if (!in_chunk && grepl("^(```|~~~)\\{r([ ,}].*)?\\}$", trimws(line))) {
      in_chunk <- TRUE
      fence <- substr(trimws(line), 1L, 3L)
      current <- character()
    } else if (in_chunk && identical(trimws(line), fence)) {
      chunks[[length(chunks) + 1L]] <- current
      in_chunk <- FALSE
    } else if (in_chunk) {
      current <- c(current, line)
    }
  }
  if (in_chunk) stop("Kapanmamış R kod bloğu")
  chunks
}

failures <- character()
total_chunks <- 0L
cat(if (identical(Sys.getenv("BOOK_SMOKE"), "1")) "Mode: SMOKE (64 replications)\n" else "Mode: REFERENCE\n")
for (file in files) {
  old_dir <- getwd()
  graphics_file <- tempfile(pattern = "book-r-lab-", fileext = ".pdf")
  grDevices::cairo_pdf(graphics_file)
  result <- tryCatch({
    setwd(dirname(file))
    chunks <- extract_r_chunks(readLines(file, warn = FALSE, encoding = "UTF-8"))
    if (length(chunks) == 0L) stop("R kod bloğu bulunamadı")
    total_chunks <- total_chunks + length(chunks)
    lab_env <- new.env(parent = globalenv())
    for (chunk in chunks) {
      eval(parse(text = chunk, keep.source = TRUE), envir = lab_env)
    }
    NULL
  }, error = function(e) conditionMessage(e), finally = {
    setwd(old_dir)
    grDevices::dev.off()
    unlink(graphics_file)
  })
  if (!is.null(result)) failures <- c(failures, paste(basename(file), result, sep = ": "))
  else cat(sprintf("PASS %s (%d chunks)\n", basename(file), length(chunks)))
}

if (length(failures) > 0L) {
  writeLines(failures, con = stderr())
  quit(status = 1L)
}

cat(sprintf("R lab checks passed for %d file(s), %d chunks.\n", length(files), total_chunks))
