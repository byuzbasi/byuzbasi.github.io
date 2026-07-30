#!/usr/bin/env python3

import unittest

from tools import sync_openalex_publications as sync


class OpenAlexBibSyncTests(unittest.TestCase):
    def setUp(self):
        self.work = {
            "id": "https://openalex.org/W123",
            "doi": "https://doi.org/10.1000/TEST.1",
            "display_name": "A New Statistical Method",
            "publication_year": 2026,
            "type": "article",
            "is_retracted": False,
            "is_paratext": False,
            "authorships": [
                {"author": {"display_name": "Bahadır Yüzbaşı"}},
                {"author": {"display_name": "Ada Lovelace"}},
            ],
            "primary_location": {"source": {"display_name": "Journal of Testing"}},
            "biblio": {
                "volume": "12",
                "issue": "3",
                "first_page": "10",
                "last_page": "21",
            },
        }

    def test_existing_bibtex_is_detected_without_reformatting(self):
        bib = """@article{existing,\n\ttitle = {{A} New Statistical Method},\n\tdoi = {10.1000/test.1},\n}\n"""
        dois, titles, _ = sync.existing_identifiers(bib)
        self.assertIn("10.1000/test.1", dois)
        self.assertIn("a new statistical method", titles)
        self.assertEqual(sync.select_missing_works([self.work], dois, titles), [])

    def test_missing_work_is_rendered_as_bibtex(self):
        selected = sync.select_missing_works([self.work], set(), set())
        self.assertEqual(len(selected), 1)
        rendered = sync.format_bib_entry(selected[0], set())
        self.assertIn("@article{yuzbasi_new_2026,", rendered)
        self.assertIn("author = {Bahadır Yüzbaşı and Ada Lovelace}", rendered)
        self.assertIn("doi = {10.1000/test.1}", rendered)
        self.assertIn("pages = {10--21}", rendered)

    def test_auto_import_block_is_idempotent_for_empty_update(self):
        bib = "@article{existing,\n\ttitle = {Existing},\n}\n"
        self.assertEqual(sync.append_entries(bib, []), bib)


if __name__ == "__main__":
    unittest.main()
