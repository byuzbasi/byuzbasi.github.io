# Bölüm 20: kalıcı paket dosyası oluşturmadan metadata ve ad alanı öğretimi.

# Bu tanımlayıcı yalnızca bellek içi DCF örneğine aittir. Yaşayan paketin adı,
# yazarı veya lisansı hakkında karar oluşturmaz.
synthetic_identifier <- "pkgogretim"
example_is_project_metadata <- FALSE

description_text <- paste(
  "Package: pkgogretim",
  "Type: Package",
  "Title: Synthetic Metadata Used Only in a Teaching Example",
  "Version: 0.0.0.9000",
  paste0(
    "Authors@R: person(\"Ada\", \"Ornek\", ",
    "email = \"ada@example.invalid\", role = c(\"aut\", \"cre\"))"
  ),
  "Description: Demonstrates DCF fields in memory without creating a package.",
  "    It is not metadata for the living package developed in the book.",
  "License: MIT + file LICENSE",
  "Encoding: UTF-8",
  "Depends: R (>= 4.3.0)",
  "Imports: stats",
  "Suggests: testthat, knitr",
  "LinkingTo: Rcpp",
  sep = "\n"
)

description_connection <- textConnection(description_text)
metadata <- read.dcf(description_connection, all = TRUE)
if (isOpen(description_connection)) {
  close(description_connection)
}

dependency_fields <- c("Depends", "Imports", "Suggests", "LinkingTo")
dependency_roles <- data.frame(
  field = dependency_fields,
  installed_with_package = c(TRUE, TRUE, FALSE, TRUE),
  attached_for_user = c(TRUE, FALSE, FALSE, FALSE),
  typical_role = c(
    "minimum R or attached runtime dependency",
    "runtime namespace dependency",
    "tests, examples, vignettes, or optional features",
    "headers required while compiling source"
  ),
  stringsAsFactors = FALSE
)

split_dependency_names <- function(value) {
  pieces <- trimws(strsplit(value, ",", fixed = TRUE)[[1L]])
  trimws(sub("\\s*\\(.*\\)$", "", pieces))
}
dependency_names <- lapply(
  dependency_fields,
  function(field) split_dependency_names(metadata[1L, field])
)
names(dependency_names) <- dependency_fields

# Kurulu temel paketin metadata ve ad alanını yalnızca okuruz. Hiçbir dosya,
# paket kütüphanesi ya da R seçeneği değiştirilmez.
stats_metadata <- utils::packageDescription("stats")
stats_exports <- getNamespaceExports("stats")

namespace_policy <- data.frame(
  directive = c("export", "importFrom", "useDynLib"),
  responsibility = c(
    "supported public names",
    "specific external names used internally",
    "registered native routines and symbol policy"
  ),
  generated_here = FALSE,
  stringsAsFactors = FALSE
)

required_fields <- c(
  "Package", "Title", "Version", "Authors@R", "Description", "License",
  "Encoding", dependency_fields
)
package_name_is_syntactic <- grepl(
  "^[A-Za-z][A-Za-z0-9.]*[A-Za-z0-9]$",
  metadata[1L, "Package"]
)

ch20_result <- identical(metadata[1L, "Package"], synthetic_identifier) &&
  identical(example_is_project_metadata, FALSE) &&
  all(required_fields %in% colnames(metadata)) &&
  package_name_is_syntactic &&
  identical(dependency_names$Imports, "stats") &&
  identical(sort(dependency_names$Suggests), c("knitr", "testthat")) &&
  identical(stats_metadata$Package, "stats") &&
  "lm" %in% stats_exports &&
  all(!namespace_policy$generated_here) &&
  !file.exists(file.path(getwd(), "DESCRIPTION")) &&
  !file.exists(file.path(getwd(), "NAMESPACE"))

if (!isTRUE(ch20_result)) {
  stop("Bölüm 20 bellek içi metadata denetimi başarısız.", call. = FALSE)
}

cat("Bölüm 20: DCF, bağımlılık rolleri ve salt okunur ad alanı geçti.\n")
