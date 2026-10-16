{{ config(
    post_hook=[
        "alter table {{ this }} set row filter {{ this.database }}.{{ this.schema }}.agency_row_filter on (agency_id)"
    ]
) }}

-- The broker work list: one row per renewing account, ranked by risk inside each agency.
{% set weights = flag_weights() %}
with scored as (
    select
        c.*,
        (
            {% for f in flag_names() %}
            case when flag_{{ f }} then {{ weights[f] }} else 0 end {{ '+' if not loop.last }}
            {% endfor %}
        ) + least(greatest(coalesce(premium_change_pct, 0), 0) / 10, 3) as risk_score,
        concat_ws(', ',
            {% for f in flag_names() %}
            case when flag_{{ f }} then '{{ f | replace("_", " ") }}' end {{ ',' if not loop.last }}
            {% endfor %}
        ) as reasons
    from {{ ref('fct_renewal_changes') }} c
)

select
    agency_id,
    rank() over (partition by agency_id order by risk_score desc, premium_change desc) as agency_rank,
    round(risk_score, 1) as risk_score,
    case when risk_score >= 4 then 'review now' when risk_score >= 2 then 'review' else 'routine' end as priority,
    date_check_failed or policy_match_failed or low_confidence_read or missing_key_field
        as needs_data_check,
    pair_id,
    policy_number,
    insured_name,
    renewal_effective_date,
    prior_premium,
    renewal_premium,
    premium_change_pct,
    reasons,
    any_scanned,
    prior_document_id,
    renewal_document_id
from scored
