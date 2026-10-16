-- Every flagged change with the page and text it came from, for both years.
-- A broker can open the cited page and check the number in seconds.
{% set field_for = {
    'large_premium_increase': 'annual_premium', 'premium_increase': 'annual_premium',
    'deductible_raised': 'collision_deductible', 'liability_lowered': 'liability_limit',
    'coverage_dropped': 'optional_coverages', 'driver_added': 'drivers',
    'vehicle_changed': 'vehicle', 'carrier_changed': 'carrier'} %}

with flags as (
    {% for f, field in field_for.items() %}
    select pair_id, agency_id, prior_document_id, renewal_document_id,
           '{{ f }}' as change_type, '{{ field }}' as field
    from {{ ref('fct_renewal_changes') }}
    where flag_{{ f }}
    {{ 'union all' if not loop.last }}
    {% endfor %}
)

select
    fl.pair_id,
    fl.agency_id,
    fl.change_type,
    fl.field,
    pe.value as prior_value,
    fl.prior_document_id,
    pe.page as prior_page,
    pe.evidence as prior_evidence,
    pe.evidence_on_page as prior_evidence_verified,
    re.value as renewal_value,
    fl.renewal_document_id,
    re.page as renewal_page,
    re.evidence as renewal_evidence,
    re.evidence_on_page as renewal_evidence_verified
from flags fl
left join {{ ref('int_extracted_fields') }} pe
    on pe.document_id = fl.prior_document_id and pe.field = fl.field
left join {{ ref('int_extracted_fields') }} re
    on re.document_id = fl.renewal_document_id and re.field = fl.field
