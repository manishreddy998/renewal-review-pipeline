# Data sources

## FSRA Ontario Automobile Policy (OAP 1)

- Publisher: Financial Services Regulatory Authority of Ontario (FSRA)
- Version: OAP1-EN.5, approved for use on or after July 1, 2026
- File: https://www.fsrao.ca/media/28946/download
- Landing page: https://www.fsrao.ca/oap-1-ontario-automobile-policy-owners-policy
- SHA-256 when first fetched (Oct 16, 2026): a2c54ba6342e79190f449398daa313c30f6b9253c8846391c7ab329282566117

### Why we use it

OAP 1 is the standard owner's auto policy that every Ontario insurer must use. It gives us the
real coverage names, section numbers and wording, so our synthetic policies look like the real
thing and use the right terms.

### License notes

FSRA publishes this form publicly for insurers, brokers and the public. FSRA content is
Crown copyright (King's Printer for Ontario). We do not store or redistribute the PDF in this
repo. The fetch step downloads it straight from FSRA and checks the hash. We only use it as a
reference for field names and coverage wording. No part of the form is presented as a real
policy for any person.

## Synthetic policies

All policy documents in this project are made up by `src/renewal_review/synthetic.py`.
No real customer, broker or insurer data is used. Every generated page carries the stamp
"SYNTHETIC TEST DATA, NOT A REAL POLICY".
