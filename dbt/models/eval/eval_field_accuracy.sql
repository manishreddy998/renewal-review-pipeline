-- Field by field accuracy against the answer key, split by agency layout and by scanned or not.
{% set fields = ['policy_number', 'insured_name', 'carrier', 'effective_date', 'vehicle_year', 'vehicle',
                 'liability_limit', 'collision_deductible', 'optional_coverages', 'drivers', 'annual_premium'] %}
with pairs as (
    {% for f in fields %}
    select
        t.document_id,
        t.agency_id,
        case when t.scanned then 'scanned' else 'digital' end as document_type,
        '{{ f }}' as field,
        cast(e.{{ f }} as string) as extracted,
        cast(t.{{ f }} as string) as expected
    from {{ ref('eval_truth_policies') }} t
    left join {{ ref('int_policy_extracted') }} e using (document_id)
    {{ 'union all' if not loop.last }}
    {% endfor %}
)

select
    field,
    agency_id,
    document_type,
    count(*) as documents,
    sum(case when extracted <=> expected then 1 else 0 end) as correct,
    round(avg(case when extracted <=> expected then 1.0 else 0.0 end), 4) as accuracy
from pairs
group by grouping sets ((field), (field, agency_id), (field, document_type), ())
