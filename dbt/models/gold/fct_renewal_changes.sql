-- Last year against the renewal for every pair, with change flags from the extracted values.
with p as (select * from {{ ref('int_policy_extracted') }} where policy_version = 'prior'),
     r as (select * from {{ ref('int_policy_extracted') }} where policy_version = 'renewal')

select
    p.pair_id,
    p.agency_id,
    r.policy_number,
    r.insured_name,
    p.document_id as prior_document_id,
    r.document_id as renewal_document_id,
    p.carrier as prior_carrier,
    r.carrier as renewal_carrier,
    r.effective_date as renewal_effective_date,
    p.annual_premium as prior_premium,
    r.annual_premium as renewal_premium,
    r.annual_premium - p.annual_premium as premium_change,
    p.liability_limit as prior_liability_limit,
    r.liability_limit as renewal_liability_limit,
    p.collision_deductible as prior_collision_deductible,
    r.collision_deductible as renewal_collision_deductible,
    p.optional_coverages as prior_coverages,
    r.optional_coverages as renewal_coverages,
    p.scanned or r.scanned as any_scanned,
    p.effective_date as prior_effective_date,
    -- A renewal starts one year after last year's term. If the two dates disagree, one of them
    -- was misread, so a person should look before trusting the comparison.
    coalesce(r.effective_date != add_months(p.effective_date, 12), true) as date_check_failed,
    p.policy_number is null or r.policy_number is null or p.policy_number != r.policy_number
        as policy_match_failed,
    p.low_confidence_read or r.low_confidence_read as low_confidence_read,
    p.missing_key_field or r.missing_key_field as missing_key_field,
    {{ renewal_flags('p', 'r') }}
from p
join r using (pair_id)
