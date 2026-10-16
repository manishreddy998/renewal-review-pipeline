-- Precision and recall of each change flag. The truth flags come from the answer key values
-- with the exact same rules, so a miss here is caused by extraction, not by the rule.
with tp as (select * from {{ ref('eval_truth_policies') }} where policy_version = 'prior'),
     tr as (select * from {{ ref('eval_truth_policies') }} where policy_version = 'renewal'),
truth as (
    select tp.pair_id, {{ renewal_flags('tp', 'tr') }}
    from tp join tr using (pair_id)
),
pred as (select * from {{ ref('fct_renewal_changes') }}),
counts as (
    {% for f in flag_names() %}
    select
        '{{ f }}' as change_type,
        sum(case when coalesce(t.flag_{{ f }}, false) and coalesce(p.flag_{{ f }}, false) then 1 else 0 end) as true_positives,
        sum(case when not coalesce(t.flag_{{ f }}, false) and coalesce(p.flag_{{ f }}, false) then 1 else 0 end) as false_positives,
        sum(case when coalesce(t.flag_{{ f }}, false) and not coalesce(p.flag_{{ f }}, false) then 1 else 0 end) as false_negatives,
        sum(case when coalesce(t.flag_{{ f }}, false) then 1 else 0 end) as actual_changes
    from truth t
    left join pred p using (pair_id)
    {{ 'union all' if not loop.last }}
    {% endfor %}
)

select
    change_type,
    actual_changes,
    true_positives,
    false_positives,
    false_negatives,
    round(true_positives / nullif(true_positives + false_positives, 0), 4) as precision,
    round(true_positives / nullif(true_positives + false_negatives, 0), 4) as recall
from counts
union all
select
    'all changes',
    sum(actual_changes), sum(true_positives), sum(false_positives), sum(false_negatives),
    round(sum(true_positives) / nullif(sum(true_positives) + sum(false_positives), 0), 4),
    round(sum(true_positives) / nullif(sum(true_positives) + sum(false_negatives), 0), 4)
from counts
