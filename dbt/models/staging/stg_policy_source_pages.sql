-- Page level text of the public reference policy, so every term can point to a page.
select
    source_id,
    page,
    text,
    length(text) as text_chars
from {{ source('raw', 'policy_source_pages') }}
