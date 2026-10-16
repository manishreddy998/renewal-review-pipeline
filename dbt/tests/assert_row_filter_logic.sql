{{ config(enabled=target.type == 'databricks') }}
-- Try every broker against every agency. A broker must see only the agency they were granted,
-- and an unknown user must see nothing. Any row returned is a leak or a wrong block.
with brokers as (
    select principal, agency_id as granted from {{ ref('agency_access') }}
    union all
    select 'stranger@example.com', null
),
agencies as (select explode(array('AGY001', 'AGY002', 'AGY003')) as agency_id),
checks as (
    select
        b.principal,
        a.agency_id,
        {{ target.catalog }}.{{ target.schema }}.agency_can_see(b.principal, a.agency_id) as allowed,
        coalesce(b.granted = a.agency_id, false) as expected
    from brokers b cross join agencies a
)
select * from checks where allowed != expected
