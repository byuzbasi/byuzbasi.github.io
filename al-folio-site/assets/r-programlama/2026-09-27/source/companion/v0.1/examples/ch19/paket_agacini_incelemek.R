# Bölüm 19: Var olan paket ağacını değiştirmeden incelemek.
# Proje kökünden: Rscript --vanilla companion/v0.1/examples/ch19/paket_agacini_incelemek.R
args_all <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args_all, value = TRUE)
if (length(script_arg) == 1L) {
  script_path <- normalizePath(sub("^--file=", "", script_arg), mustWork = TRUE)
  project_dir <- normalizePath(file.path(dirname(script_path), "../../../.."),
                               mustWork = TRUE)
} else {
  project_dir <- normalizePath(getwd(), mustWork = TRUE)
}
package_dir <- file.path(project_dir, "companion/v0.1/capstone-package/BernoulliRuns")
required <- c("DESCRIPTION", "NAMESPACE", "R", "man", "tests", "vignettes")
present <- file.exists(file.path(package_dir, required))
stopifnot(all(present))
metadata <- read.dcf(file.path(package_dir, "DESCRIPTION"))
stopifnot(metadata[1, "Package"] == "BernoulliRuns")
print(data.frame(component = required, present = present), row.names = FALSE)
print(metadata[, c("Package", "Version", "License"), drop = FALSE])
message("Bölüm 19: PASS; paket ağacına yazılmadı.")
