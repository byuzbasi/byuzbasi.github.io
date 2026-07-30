#!/usr/bin/env python3
"""Append publications missing from the curated BibTeX file using OpenAlex.

The script deliberately preserves every existing BibTeX record byte-for-byte.
It only appends OpenAlex records whose DOI and normalized title are both absent.
The GitHub Actions workflow opens the result as a pull request for review.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable


OPENALEX_API = "https://api.openalex.org"
AUTO_IMPORT_HEADER = "% BEGIN OPENALEX AUTO-IMPORTS"
AUTO_IMPORT_FOOTER = "% END OPENALEX AUTO-IMPORTS"
SUPPORTED_TYPES = {
    "article",
    "book",
    "book-chapter",
    "dissertation",
    "editorial",
    "letter",
    "preprint",
    "proceedings-article",
    "report",
    "review",
}
TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "via",
    "with",
}


def api_get(url: str, *, timeout: int = 45) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "byuzbasi.github.io publication sync (https://byuzbasi.github.io)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OpenAlex request failed: {url}\n{exc}") from exc


def fetch_openalex_works(orcid: str) -> list[dict[str, Any]]:
    author_url = f"{OPENALEX_API}/authors/orcid:{urllib.parse.quote(orcid)}"
    author = api_get(author_url)
    author_id = author.get("id")
    if not author_id:
        raise RuntimeError(f"OpenAlex returned no author ID for ORCID {orcid}.")

    works: list[dict[str, Any]] = []
    cursor = "*"
    while cursor:
        query = urllib.parse.urlencode(
            {
                "filter": f"authorships.author.id:{author_id}",
                "per-page": 200,
                "cursor": cursor,
                "sort": "publication_date:desc",
            }
        )
        payload = api_get(f"{OPENALEX_API}/works?{query}")
        works.extend(payload.get("results", []))
        next_cursor = payload.get("meta", {}).get("next_cursor")
        cursor = next_cursor if next_cursor and next_cursor != cursor else ""
    return works


def extract_bib_field(entry: str, field: str) -> str:
    match = re.search(rf"(?mi)^\s*{re.escape(field)}\s*=\s*([{{\"])", entry)
    if not match:
        return ""
    opening = match.group(1)
    start = match.end()
    if opening == '"':
        escaped = False
        chars: list[str] = []
        for char in entry[start:]:
            if char == '"' and not escaped:
                break
            chars.append(char)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        return "".join(chars).strip()

    depth = 1
    chars = []
    for char in entry[start:]:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                break
        chars.append(char)
    return "".join(chars).strip()


def iter_bib_entries(text: str) -> Iterable[str]:
    starts = list(re.finditer(r"(?m)^@\w+\s*\{", text))
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        yield text[start.start() : end]


def normalize_doi(value: str) -> str:
    doi = html.unescape(value).strip().lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.rstrip(".,;)}] ")


def normalize_text(value: str) -> str:
    text = html.unescape(value)
    text = text.translate(
        str.maketrans(
            {
                "ı": "i",
                "İ": "I",
                "ş": "s",
                "Ş": "S",
                "ğ": "g",
                "Ğ": "G",
                "ç": "c",
                "Ç": "C",
                "ö": "o",
                "Ö": "O",
                "ü": "u",
                "Ü": "U",
            }
        )
    )
    # Remove common BibTeX case-protection and accent syntax for matching only.
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[\"'`^~=.uvHckbdtr]\s*\{?([A-Za-z])\}?", r"\1", text)
    text = text.replace("{", "").replace("}", "").replace("\\", "")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def existing_identifiers(text: str) -> tuple[set[str], set[str], set[str]]:
    dois: set[str] = set()
    titles: set[str] = set()
    keys = set(re.findall(r"(?mi)^@\w+\s*\{\s*([^,\s]+)", text))
    for entry in iter_bib_entries(text):
        doi = normalize_doi(extract_bib_field(entry, "doi"))
        title = normalize_text(extract_bib_field(entry, "title"))
        if doi:
            dois.add(doi)
        if title:
            titles.add(title)
    return dois, titles, keys


def clean_bib_value(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("{", "").replace("}", "")


def work_doi(work: dict[str, Any]) -> str:
    return normalize_doi(work.get("doi") or "")


def work_title(work: dict[str, Any]) -> str:
    return clean_bib_value(work.get("title") or work.get("display_name") or "")


def work_authors(work: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for authorship in work.get("authorships") or []:
        name = clean_bib_value((authorship.get("author") or {}).get("display_name"))
        if name and name not in names:
            names.append(name)
    return names


def slug(value: str, fallback: str) -> str:
    normalized = normalize_text(value).replace(" ", "_")
    return normalized or fallback


def make_key(work: dict[str, Any], used_keys: set[str]) -> str:
    authors = work_authors(work)
    lead = authors[0].split()[-1] if authors else "openalex"
    words = [
        word
        for word in normalize_text(work_title(work)).split()
        if word not in TITLE_STOPWORDS
    ]
    keyword = words[0] if words else "work"
    year = str(work.get("publication_year") or "undated")
    base = f"{slug(lead, 'openalex')}_{slug(keyword, 'work')}_{year}"
    candidate = base
    suffix = 2
    while candidate in used_keys:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used_keys.add(candidate)
    return candidate


def bib_type(work_type: str) -> str:
    if work_type == "book":
        return "book"
    if work_type == "book-chapter":
        return "incollection"
    if work_type == "proceedings-article":
        return "inproceedings"
    if work_type in {"article", "editorial", "letter", "review"}:
        return "article"
    return "misc"


def source_name(work: dict[str, Any]) -> str:
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    return clean_bib_value(source.get("display_name"))


def format_bib_entry(work: dict[str, Any], used_keys: set[str]) -> str:
    entry_type = bib_type(str(work.get("type") or ""))
    key = make_key(work, used_keys)
    title = work_title(work)
    authors = work_authors(work)
    year = work.get("publication_year")
    doi = work_doi(work)
    openalex_id = clean_bib_value(work.get("id"))
    source = source_name(work)
    biblio = work.get("biblio") or {}

    fields: list[tuple[str, str]] = [
        ("title", title),
        ("author", " and ".join(authors)),
        ("year", str(year or "")),
    ]
    if source:
        if entry_type == "article":
            fields.append(("journal", source))
        elif entry_type in {"incollection", "inproceedings"}:
            fields.append(("booktitle", source))
        else:
            fields.append(("howpublished", source))
    for field_name, source_field in (("volume", "volume"), ("number", "issue")):
        value = clean_bib_value(biblio.get(source_field))
        if value:
            fields.append((field_name, value))
    first_page = clean_bib_value(biblio.get("first_page"))
    last_page = clean_bib_value(biblio.get("last_page"))
    if first_page:
        fields.append(("pages", f"{first_page}--{last_page}" if last_page and last_page != first_page else first_page))
    if doi:
        fields.extend((("doi", doi), ("url", f"https://doi.org/{doi}")))
    elif openalex_id:
        fields.append(("url", openalex_id))
    if openalex_id:
        fields.append(("openalex", openalex_id))

    rendered = [f"@{entry_type}{{{key},"]
    rendered.extend(f"\t{name} = {{{value}}}," for name, value in fields if value)
    rendered.append("}")
    return "\n".join(rendered)


def select_missing_works(
    works: Iterable[dict[str, Any]],
    existing_dois: set[str],
    existing_titles: set[str],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_dois = set(existing_dois)
    seen_titles = set(existing_titles)
    for work in works:
        if work.get("is_retracted") or work.get("is_paratext"):
            continue
        if work.get("type") not in SUPPORTED_TYPES:
            continue
        title = work_title(work)
        normalized_title = normalize_text(title)
        doi = work_doi(work)
        if not title or not work.get("publication_year") or not work_authors(work):
            continue
        if (doi and doi in seen_dois) or normalized_title in seen_titles:
            continue
        selected.append(work)
        if doi:
            seen_dois.add(doi)
        seen_titles.add(normalized_title)
    return selected


def append_entries(text: str, entries: list[str]) -> str:
    if not entries:
        return text
    block = "\n\n".join(entries)
    if AUTO_IMPORT_FOOTER in text:
        return text.replace(AUTO_IMPORT_FOOTER, f"{block}\n\n{AUTO_IMPORT_FOOTER}", 1)
    return f"{text.rstrip()}\n\n{AUTO_IMPORT_HEADER}\n{block}\n{AUTO_IMPORT_FOOTER}\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orcid", default="0000-0002-6196-3201")
    parser.add_argument("--bib", type=Path, default=Path("publications.bib"))
    parser.add_argument(
        "--mirror",
        type=Path,
        default=Path("al-folio-site/_bibliography/papers.bib"),
        help="Site bibliography mirror updated after the curated source.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bib_path = args.bib.resolve()
    mirror_path = args.mirror.resolve()
    if not bib_path.is_file():
        print(f"BibTeX source not found: {bib_path}", file=sys.stderr)
        return 2

    original = bib_path.read_text(encoding="utf-8")
    dois, titles, keys = existing_identifiers(original)
    works = fetch_openalex_works(args.orcid)
    missing = select_missing_works(works, dois, titles)
    entries = [format_bib_entry(work, keys) for work in missing]
    updated = append_entries(original, entries)

    print(
        f"OpenAlex returned {len(works)} works; "
        f"{len(missing)} publication(s) are missing from {bib_path.name}."
    )
    if args.dry_run:
        for entry in entries:
            print(f"\n{entry}")
        return 0
    if updated == original:
        print("No bibliography changes required.")
        return 0

    bib_path.write_text(updated, encoding="utf-8")
    mirror_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bib_path, mirror_path)
    print(f"Updated {bib_path} and {mirror_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
