-- Of the accounts where at least one field was read wrong, how many did the pipeline mark
-- "needs data check"? And how many correct accounts were marked for nothing?
with wrong as (
    select distinct d.pair_id
    from {{ ref('eval_field_errors') }} e
    join {{ ref('stg_documents') }} d using (document_id)
),
q as (
    select q.pair_id, q.needs_data_check, w.pair_id is not null as has_error
    from {{ ref('mart_renewal_queue') }} q
    left join wrong w using (pair_id)
)
select
    count(*) as accounts,
    sum(case when has_error then 1 else 0 end) as accounts_with_a_wrong_field,
    sum(case when has_error and needs_data_check then 1 else 0 end) as caught_by_checks,
    sum(case when not has_error and needs_data_check then 1 else 0 end) as checked_but_fine,
    sum(case when needs_data_check then 1 else 0 end) as marked_for_check
from q
