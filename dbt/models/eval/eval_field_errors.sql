-- Every wrong field, to see exactly what went wrong.
{% set fields = ['policy_number', 'insured_name', 'carrier', 'effective_date', 'vehicle_year', 'vehicle',
                 'liability_limit', 'collision_deductible', 'optional_coverages', 'drivers', 'annual_premium'] %}
{% for f in fields %}
select
    t.document_id, t.agency_id, t.scanned, '{{ f }}' as field,
    cast(e.{{ f }} as string) as extracted, cast(t.{{ f }} as string) as expected
from {{ ref('eval_truth_policies') }} t
left join {{ ref('int_policy_extracted') }} e using (document_id)
where not (cast(e.{{ f }} as string) <=> cast(t.{{ f }} as string))
{{ 'union all' if not loop.last }}
{% endfor %}
