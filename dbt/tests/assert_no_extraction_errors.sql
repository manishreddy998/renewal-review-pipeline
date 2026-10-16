{{ config(enabled=target.type == 'databricks') }}
select document_id, error_message
from {{ ref('int_extraction_raw') }}
where prompt_version = '{{ var("prompt_version") }}' and error_message is not null
