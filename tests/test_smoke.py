import tempfile
import unittest
from pathlib import Path

import bib_literature_audit as bla


SAMPLE_BIB = r"""
@article{smith2024example,
  author  = {Smith, Jane},
  title   = {An Example Article},
  journal = {Example Journal},
  year    = {2024}
}

@misc{project2024page,
  title        = {Example Project Factsheet},
  year         = {2024},
  howpublished = {Project factsheet},
  url          = {https://example.org/factsheet}
}
"""


class SmokeTests(unittest.TestCase):
    def test_parse_and_classify(self):
        entries, skipped, warnings = bla.parse_bibtex(SAMPLE_BIB)
        self.assertEqual(skipped, 0)
        self.assertEqual(warnings, [])
        self.assertEqual(len(entries), 2)
        self.assertEqual(bla.classify_reference(entries[0]).kind, "journal_article")
        self.assertEqual(bla.classify_reference(entries[1]).kind, "web_resource")

    def test_offline_audit_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bib = tmp_path / "sample.bib"
            out = tmp_path / "audit"
            bib.write_text(SAMPLE_BIB, encoding="utf-8")
            code = bla.main([str(bib), "--output-dir", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue((out / "report.md").exists())
            self.assertTrue((out / "report.json").exists())
            self.assertTrue((out / "references_audit.csv").exists())
            self.assertTrue((out / "manual_review.csv").exists())


if __name__ == "__main__":
    unittest.main()
