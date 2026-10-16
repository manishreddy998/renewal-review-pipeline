{{ config(enabled=target.type == 'databricks') }}
-- depends_on: {{ ref('mart_renewal_queue') }}
-- The work list table must carry the agency row filter in Unity Catalog.
select 'missing row filter' as problem
from (select 1)
where not exists (
    select 1
    from {{ target.catalog }}.information_schema.row_filters
    where table_schema = '{{ target.schema }}'
      and table_name = 'mart_renewal_queue'
)
