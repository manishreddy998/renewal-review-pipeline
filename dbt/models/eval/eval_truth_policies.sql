-- Answer key in the same shape and cleaning as the extracted values.
select
    d.document_id,
    t.pair_id,
    t.agency_id,
    t.policy_version,
    d.scanned,
    t.policy_number,
    trim(regexp_replace(lower(t.insured_name), '\\s*\\(fictional\\)', '')) as insured_name,
    trim(regexp_replace(lower(t.carrier), '\\s*\\(fictional\\)', '')) as carrier,
    t.effective_date,
    t.vehicle_year,
    lower(t.vehicle) as vehicle,
    t.liability_limit,
    t.collision_deductible,
    nullif(t.optional_coverages, '') as optional_coverages,
    t.drivers,
    cast(t.annual_premium as decimal(12, 2)) as annual_premium
from {{ ref('stg_policy_pairs') }} t
join {{ ref('stg_documents') }} d
    on d.pair_id = t.pair_id and d.policy_version = t.policy_version
