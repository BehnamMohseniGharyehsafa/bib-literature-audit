# Bib Literature Audit

A conservative, reproducible Python tool for auditing BibTeX bibliographies used in academic literature reviews and research projects.

The tool classifies reference types, checks structural metadata, detects duplicate records, verifies existing DOI values, searches for missing scholarly DOIs, validates URLs, and can generate a DOI-enriched copy of the bibliography without modifying the original file.

## Key features

- Uses only the Python standard library at runtime.
- Parses and audits `.bib` files without modifying the source file.
- Distinguishes journal articles, conference papers, technical reports, web resources, datasets, books, theses, software, standards, and other document types.
- Does not treat every URL as a website and does not treat every missing DOI as an error.
- Detects exact citation-key duplicates, case-only key collisions, duplicate DOI values, normalized-title duplicates, and conservative fuzzy duplicate candidates.
- Verifies existing DOI values against Crossref and, where appropriate, DataCite.
- Searches Crossref for missing DOI values only for suitable scholarly reference classes.
- Compares title, first author, publication year, source, and Crossref work type before automatically accepting a DOI.
- Rejects incompatible preprint or posted-content DOI candidates for journal-article records.
- Sends ambiguous candidates to a manual-review table rather than silently modifying the bibliography.
- Validates URLs while distinguishing reachable pages, access restrictions, broken links, server errors, and network-inconclusive checks.
- Produces Markdown, JSON, and CSV audit reports plus an optional enriched BibTeX file.
- Records only the input filename in reports, not the user's absolute local file path.
- Does not require or transmit an email address or other user identifier.

## Repository contents

```text
bib-literature-audit/
├── bib_literature_audit.py
├── references.bib
├── references_audit/
│   ├── console_summary.txt
│   ├── manual_review.csv
│   ├── references_audit.csv
│   ├── references.enriched.bib
│   ├── report.json
│   └── report.md
├── tests/
│   └── test_smoke.py
├── .github/workflows/ci.yml
├── .gitignore
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── README.md
```

`references.bib` is included as a real bibliography example. The `references_audit/` directory contains a snapshot of the audit output generated from that file. Online metadata services can change over time, so future runs may return slightly different DOI candidates or landing URLs.

## Requirements

- Python 3.10 or newer
- Internet access only for DOI verification, DOI discovery, DOI resolution, and URL validation

No third-party Python package is required for normal script execution.

## Quick start

### Offline bibliography audit

```bash
python bib_literature_audit.py references.bib
```

This performs parsing, classification, structural metadata checks, duplicate analysis, URL syntax checks, and other offline quality-control operations.

### DOI verification and enrichment

```bash
python bib_literature_audit.py references.bib --online --write-enriched
```

### Full audit including non-paper URL validation

```bash
python bib_literature_audit.py references.bib --online --check-urls --write-enriched
```

### PowerShell

```powershell
python bib_literature_audit.py "references.bib" --online --check-urls --write-enriched
```

## Optional installation as a command

The repository includes a minimal `pyproject.toml`. From the repository root:

```bash
python -m pip install .
```

You can then run:

```bash
bib-literature-audit references.bib --online --check-urls --write-enriched
```

## Output files

By default, the script creates `<input-stem>_audit/`.

```text
references_audit/
├── report.md
├── report.json
├── references_audit.csv
├── manual_review.csv
└── references.enriched.bib
```

The enriched bibliography is created only when `--write-enriched` is supplied.

### `report.md`

Human-readable summary of reference classification, quality checks, duplicate groups, DOI results, URL results, and methodology notes.

### `report.json`

Machine-readable form of the complete audit for reproducibility or downstream processing.

### `references_audit.csv`

One row per bibliography entry with its classification, metadata quality indicators, DOI status, matching diagnostics, and URL-check results.

### `manual_review.csv`

A deliberately small queue of records requiring human judgement, such as ambiguous DOI candidates or duplicate records. The tool does not automatically accept uncertain DOI matches or delete duplicate entries.

### `references.enriched.bib`

A copy of the input bibliography containing only DOI values accepted at high confidence. The original `.bib` file is never overwritten.

## Reference classification

The classifier is bibliographic rather than URL-based. For example:

- a journal article with a publisher URL remains a `journal_article`;
- a conference contribution remains a `conference_paper`;
- a project PDF is normally a `technical_report`;
- an HTML project page can be a `web_resource`;
- a DOI-identified research dataset can be classified as a `dataset`.

This distinction is important because DOI expectations differ across reference classes.

## DOI matching strategy

For missing DOI values, the tool queries Crossref for eligible scholarly works and evaluates candidate metadata using:

1. normalized title similarity;
2. first-author agreement;
3. publication-year consistency;
4. journal or proceedings similarity;
5. Crossref work-type compatibility;
6. the score margin between the best and competing candidates.

A candidate must satisfy conservative acceptance rules before it is inserted automatically. Otherwise it is written to `manual_review.csv`.

Existing DOI values are checked against Crossref and, where relevant, DataCite. DOI resolution through `doi.org` is used to identify the current landing page when possible.

## Example audit snapshot

The bundled `references.bib` contains 309 records. In the included online audit snapshot:

| Result | Count |
|---|---:|
| Journal articles | 284 |
| Conference papers | 10 |
| Technical reports | 10 |
| Web resources | 3 |
| Dataset | 1 |
| Other document | 1 |
| DOI-search-eligible scholarly references | 294 |
| Existing DOI values verified | 2 |
| High-confidence missing DOIs discovered | 258 |
| DOI candidates requiring manual review | 29 |
| No Crossref candidate found | 5 |
| Trusted scholarly references with DOI | 260 |
| Exact normalized-title duplicate groups | 1 |

These values are an example snapshot, not fixed expectations for future runs.

## Important design principle

The program is intentionally conservative. A false-positive DOI is more damaging to a scholarly bibliography than leaving an uncertain DOI unresolved. Therefore:

- uncertain matches are not written automatically;
- preprint DOI values are not substituted automatically for final journal articles;
- missing DOI values are not considered defects for reference classes that may legitimately lack them;
- duplicate records are reported but never deleted automatically.

## Command-line options

```bash
python bib_literature_audit.py --help
```

Important options include:

```text
--online               Verify existing DOIs and search for missing scholarly DOIs
--check-urls           Validate URLs associated with non-paper references
--check-paper-urls     Also validate URLs attached to scholarly papers
--write-enriched       Write a DOI-enriched copy of the bibliography
--output-dir PATH      Choose the output directory
--accept-threshold N   Adjust the automatic DOI acceptance threshold
--crossref-rows N      Number of Crossref candidates evaluated per search
--timeout N            HTTP timeout in seconds
--delay N              Minimum delay between HTTP requests
--retries N            Number of retries for transient HTTP/network failures
--no-search-missing    Verify existing DOI values without searching for missing ones
--version              Show the program version
```

The default DOI acceptance threshold is intentionally strict. Lower it only if you understand the increased risk of false-positive matches.

## Testing

Run the included standard-library tests with:

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow compiles the program, runs the smoke tests, and performs an offline audit of the bundled bibliography on Python 3.10 through 3.13.

## Reproducibility and limitations

The report includes the source bibliography filename, file size, text encoding, and SHA-256 digest. These allow a specific bibliography snapshot to be identified without exposing an absolute local filesystem path.

Online DOI and URL results depend on external services and network conditions. Crossref, DataCite, publisher metadata, DOI landing pages, and project websites may change after an audit is generated. Manual review remains appropriate for ambiguous records.

This tool performs bibliographic quality assurance. It is not a replacement for a documented literature-search protocol, study-screening protocol, risk-of-bias assessment, or a formal systematic-review framework.

## License

Released under the MIT License. See [`LICENSE`](LICENSE).

## Citation

Academic users can use the repository metadata in [`CITATION.cff`](CITATION.cff). GitHub will expose this through its **Cite this repository** interface.
