-- One typed row per document, ready to compare across years.
select
    d.document_id,
    d.pair_id,
    d.agency_id,
    d.policy_version,
    d.scanned,
    max(case when f.field = 'policy_number' then f.value end) as policy_number,
    max(case when f.field = 'insured_name' then f.value end) as insured_name,
    max(case when f.field = 'carrier' then f.value end) as carrier,
    try_cast(max(case when f.field = 'effective_date' then f.value end) as date) as effective_date,
    try_cast(max(case when f.field = 'vehicle_year' then f.value end) as int) as vehicle_year,
    max(case when f.field = 'vehicle' then f.value end) as vehicle,
    try_cast(max(case when f.field = 'liability_limit' then f.value end) as bigint) as liability_limit,
    try_cast(max(case when f.field = 'collision_deductible' then f.value end) as int) as collision_deductible,
    max(case when f.field = 'optional_coverages' then f.value end) as optional_coverages,
    try_cast(max(case when f.field = 'drivers' then f.value end) as int) as drivers,
    try_cast(max(case when f.field = 'annual_premium' then f.value end) as decimal(12, 2)) as annual_premium,
    -- True when a number that drives the comparison was read by OCR with low confidence.
    coalesce(max(case when f.field in ('annual_premium', 'effective_date', 'liability_limit',
                                       'collision_deductible', 'drivers')
                       and f.ocr_confidence < {{ var('ocr_min_confidence') }} then 1 end), 0) = 1
        as low_confidence_read,
    -- True when a field that should always be on a declarations page came back empty.
    coalesce(max(case when f.field in ('policy_number', 'effective_date', 'liability_limit',
                                       'collision_deductible', 'drivers', 'annual_premium')
                       and f.value is null then 1 end), 0) = 1
        as missing_key_field
from {{ ref('stg_documents') }} d
join {{ ref('int_extracted_fields') }} f using (document_id)
group by d.document_id, d.pair_id, d.agency_id, d.policy_version, d.scanned
