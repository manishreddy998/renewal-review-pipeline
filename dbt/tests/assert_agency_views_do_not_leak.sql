-- Each agency view must hold only its own agency, and together they must cover every account
-- exactly once. Any row returned here is a leak or a gap.
with views as (
    select 'AGY001' as view_agency, agency_id, pair_id from {{ ref('renewal_queue_agy001') }}
    union all
    select 'AGY002', agency_id, pair_id from {{ ref('renewal_queue_agy002') }}
    union all
    select 'AGY003', agency_id, pair_id from {{ ref('renewal_queue_agy003') }}
)
select 'leak' as problem, view_agency, agency_id, pair_id
from views
where agency_id != view_agency
union all
select 'gap', q.agency_id, q.agency_id, q.pair_id
from {{ ref('mart_renewal_queue') }} q
left join views v on v.pair_id = q.pair_id
where v.pair_id is null
union all
select 'source agency mismatch', q.agency_id, d.agency_id, q.pair_id
from {{ ref('mart_renewal_queue') }} q
join {{ ref('stg_documents') }} d on d.document_id in (q.prior_document_id, q.renewal_document_id)
where d.agency_id != q.agency_id
