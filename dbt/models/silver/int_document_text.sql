-- Whole document text with page markers, so the model can cite pages.
select
    p.document_id,
    d.agency_id,
    array_join(
        transform(
            array_sort(collect_list(struct(p.page, p.text))),
            x -> concat('=== PAGE ', x.page, ' ===\n', x.text)
        ),
        '\n\n'
    ) as body,
    count(*) as page_count,
    max(case when p.text_method = 'ocr' then 1 else 0 end) = 1 as has_ocr
from {{ ref('stg_document_pages') }} p
join {{ ref('stg_documents') }} d using (document_id)
group by p.document_id, d.agency_id
