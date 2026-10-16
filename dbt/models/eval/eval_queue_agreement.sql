-- Does the work list put the same accounts in "review now" as the answer key would?
{% set weights = flag_weights() %}
with tp as (select * from {{ ref('eval_truth_policies') }} where policy_version = 'prior'),
     tr as (select * from {{ ref('eval_truth_policies') }} where policy_version = 'renewal'),
truth_flags as (
    select tp.pair_id, {{ renewal_flags('tp', 'tr') }} from tp join tr using (pair_id)
),
truth as (
    select
        pair_id,
        (
            {% for f in flag_names() %}
            case when flag_{{ f }} then {{ weights[f] }} else 0 end {{ '+' if not loop.last }}
            {% endfor %}
        ) + least(greatest(coalesce(premium_change_pct, 0), 0) / 10, 3) as risk_score
    from truth_flags
),
joined as (
    select
        q.pair_id,
        q.priority as predicted_priority,
        case when t.risk_score >= 4 then 'review now' when t.risk_score >= 2 then 'review' else 'routine' end as true_priority
    from {{ ref('mart_renewal_queue') }} q
    join truth t using (pair_id)
)

select
    count(*) as accounts,
    round(avg(case when predicted_priority = true_priority then 1.0 else 0.0 end), 4) as priority_agreement,
    sum(case when true_priority = 'review now' then 1 else 0 end) as true_review_now,
    sum(case when true_priority = 'review now' and predicted_priority = 'review now' then 1 else 0 end) as review_now_caught,
    sum(case when true_priority != 'review now' and predicted_priority = 'review now' then 1 else 0 end) as review_now_extra
from joined
