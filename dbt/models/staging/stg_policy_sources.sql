-- One row per public source document we use as a reference.
select
    source_id,
    title,
    publisher,
    url,
    sha256,
    page_count
from {{ source('raw', 'policy_sources') }}
