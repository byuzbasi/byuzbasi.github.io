Product Tags and the Observability of Marketplace Enforcement:
Evidence from DSA Transparency Data
Bahadır Yüzbaşı and Serkan Benk
Replication materials, version 1, 27 October 2026

REQUIREMENTS AND RUN
Python 3.9 or later. The script uses only the Python standard library.
Extract the complete archive, open a terminal in the extracted folder and run:

python3 run.py --check
python3 run.py

The first command checks input hashes, cell count and statement-frequency total.
The second reconstructs the nine result tables in results/tables and compares
them byte for byte with reference/. No package installation is required.
A run refuses to overwrite results/scope.json. To repeat, extract a fresh copy.
The original workflow took a few seconds for arithmetic on a local laptop;
execution time on other computers may differ. No random seed is needed.

DATA AND SCOPE
The data/prepared directory contains the frozen five-marketplace analytical
snapshot and its exact common-support memberships and integer weights.
There are 20,528 aggregation cells, representing a source count sum of
346,993,630 statements during September–November 2025. This total does not
represent independently observed people, products, sellers or incidents.
There is no regression, model fitting, resampling or hypothesis testing.
The product-tagged population is a separate descriptive target. Undefined
comparisons remain undefined. The public data preserve the original cells,
values, source identifiers, matching fields and weights.

DATA SOURCE
European Commission, Digital Services Act Transparency Database.
Download service: https://transparency.dsa.ec.europa.eu/explore-data/download
Documentation: https://transparency.dsa.ec.europa.eu/page/documentation
Data-package documentation:
https://dsa.pages.code.europa.eu/transparency-database/dsa-tdb/data_sources.html
The archive contains the selected frozen analytical snapshot rather than all
monthly exports or the targeted raw-archive audit. Input and archive manifests
allow the supplied files to be checked. Source-data reuse remains subject to
the original provider's terms. See Supplementary Materials Guide for meanings,
units, source-field definitions and the list of reference tables.

OUTPUTS
Nine CSV tables in results/tables, per-stratum outcome calculations and a
calculation receipt. Frequency counts are source counts. Percentage columns
end in _pct; differences are in percentage points. Empty numeric values are
undefined, not zero. Overlapping pair counts must not be added together.
