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

## How documents are rendered

`make render` turns every record into a PDF (400 documents, 2 or 3 pages each).

- Maple Lane (AGY001) uses a clean two column table with dollar amounts like `$1,000`.
- Lakeshore (AGY002) uses an all caps carrier form spread over 3 pages, with amounts like
  `1000.00 CAD` and coverage names with OAP 1 section numbers.
- Northbay (AGY003) writes a friendly letter, so the facts sit inside sentences.
- About 15 percent of documents are turned into scanned looking images: slight rotation, grey
  noise, a little blur, and no text layer. These need OCR before anything can read them.
- The stamp is printed in the header and footer of every page, plus a large watermark.
