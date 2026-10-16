# Synthetic data plan

## Goal

About 200 policy pairs (last year and renewal) spread across 3 fictional agencies. We plant
the changes ourselves, so we have a correct answer for every field. That lets us measure how
well the extraction step does, field by field.

## What is in each pair

- Policy number, agency, insured name (all fake, for example "Test Client 1001")
- Vehicle year, liability limit, collision deductible, optional coverages, number of drivers
- Annual premium
- A list of planted changes, such as a large premium increase, a raised deductible, a lower
  liability limit, a dropped coverage, an added driver or a changed vehicle

Coverage names follow the sections of the FSRA OAP 1 policy, so the documents use real terms.

## Safety rules

- Every page of every generated document carries the stamp
  "SYNTHETIC TEST DATA, NOT A REAL POLICY".
- Agency and client names are made up and marked "(fictional)".
- The generator uses a fixed seed, so the same command always gives the same data.

## Build order

1. Answer key as JSON lines (done in this step, `make synthetic`).
2. Render each policy as a 2 to 3 page PDF declarations page with the stamp in the header and
   footer of every page.
3. Add some realistic mess: different layouts per agency, scanned looking pages, and a few
   missing fields, so results are not too optimistic.
4. Load the answer key into Delta tables split by agency, for the accuracy checks later.
