# Results summary

Run on Databricks (GCP workspace, catalog `workspace`) on Oct 16, 2026. 200 synthetic clients,
400 documents, 934 pages, 3 fictional agencies. All data is synthetic test data.

## Extraction

- Endpoint: `databricks-gemini-3-5-flash` through `ai_query`, prompt version v4.
- 400 of 400 documents extracted, 0 errors.
- 171 seconds for the whole batch, about 0.43 seconds per document.
- About 693 input and 310 output tokens per document. $0.0048 per document at list price,
  $1.92 for all 400.

## Field accuracy (vs the answer key)

| Field | Accuracy |
| --- | --- |
| policy number | 100% |
| insured name | 100% |
| carrier | 100% |
| vehicle, vehicle year | 100% |
| liability limit | 100% |
| optional coverages | 100% |
| collision deductible | 99.75% |
| effective date | 99.50% |
| drivers | 99.50% |
| annual premium | 99.50% |
| **All fields** | **99.84%** (4,393 of 4,400) |

Digital PDFs: 100%. Scanned documents: 99.1%. All 7 wrong values are on scanned pages.

## Change detection (193 real changes)

| Change | Real | Precision | Recall |
| --- | --- | --- | --- |
| large premium increase | 44 | 100% | 100% |
| premium increase | 49 | 100% | 100% |
| deductible raised | 30 | 100% | 100% |
| liability lowered | 7 | 100% | 100% |
| coverage dropped | 13 | 100% | 100% |
| driver added | 23 | 100% | 100% |
| vehicle changed | 14 | 100% | 100% |
| carrier changed | 13 | 100% | 100% |

## Work list

- 71 "review now", 34 "review", 95 "routine".
- Priority matches the answer key for 200 of 200 accounts.
- 25 accounts marked "needs data check". This includes all 7 accounts with a misread value.

## Isolation and traceability

- Unity Catalog row filter on `mart_renewal_queue`, driven by the `agency_access` table.
- Tests: every broker against every agency (and an unknown user), per agency views hold only
  their own agency, and every account sits in exactly one view. 0 leaks.
- Every extracted value cites a page that exists, and 100 percent of evidence quotes are found
  on the cited page. The dbt test fails the build if this drops below 98 percent.

## Files

`renewal_queue.csv`, `change_evidence.csv`, `field_accuracy.csv`, `field_errors.csv`,
`change_detection.csv`, `queue_agreement.csv`, `data_checks.csv`, `cost.csv`.
