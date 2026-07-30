#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "${script_dir}/.." && pwd)"
source_tex="${repository_root}/CV Bahadir.tex"
profile_photo="${repository_root}/al-folio-site/assets/img/bahadir-yuzbasi.jpg"
output_pdf="${repository_root}/al-folio-site/assets/files/Bahadir-Yuzbasi-CV.pdf"
build_dir="$(mktemp -d /private/tmp/bahadir-cv-build.XXXXXX)"

cleanup() {
  rm -rf -- "${build_dir}"
}
trap cleanup EXIT

cp "${source_tex}" "${build_dir}/CV Bahadir.tex"
cp "${profile_photo}" "${build_dir}/cover_photo3_bahadir.jpeg"

(
  cd "${build_dir}"
  latexmk -pdf -interaction=nonstopmode -halt-on-error "CV Bahadir.tex"
)

mkdir -p "$(dirname -- "${output_pdf}")"
cp "${build_dir}/CV Bahadir.pdf" "${output_pdf}"
printf 'CV generated: %s\n' "${output_pdf}"
