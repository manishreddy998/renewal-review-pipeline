-- Traceability: every extracted value must point to a page that exists, and at least 98 percent
-- of quoted evidence must be found on that page.
with s as (
    select
        sum(case when value is not null and not cited_page_exists then 1 else 0 end) as bad_pages,
        avg(case when value is not null then cast(evidence_on_page as int) end) as evidence_rate
    from {{ ref('int_extracted_fields') }}
)
select * from s where bad_pages > 0 or evidence_rate < 0.98
