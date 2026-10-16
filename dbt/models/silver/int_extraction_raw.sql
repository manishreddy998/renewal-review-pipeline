{{ config(
    materialized='incremental',
    unique_key='extraction_key',
    incremental_strategy='merge'
) }}

-- One model call per document. Incremental, so a document is only sent again when it is new
-- or its text or the prompt version changes. This keeps cost down on reruns.
with todo as (
    select t.*, concat(t.document_id, ':', '{{ var("prompt_version") }}', ':', md5(t.body)) as extraction_key
    from {{ ref('int_document_text') }} t
    {% if is_incremental() %}
    where concat(t.document_id, ':', '{{ var("prompt_version") }}', ':', md5(t.body))
        not in (select extraction_key from {{ this }} where error_message is null)
    {% endif %}
),

called as (
    select
        extraction_key,
        document_id,
        agency_id,
        length(body) as input_chars,
        ai_query(
            '{{ var("extraction_endpoint") }}',
            concat({{ extraction_prompt() }}, body),
            responseFormat => '{"type": "json_object"}',
            failOnError => false
        ) as response
    from todo
)

select
    extraction_key,
    document_id,
    agency_id,
    '{{ var("extraction_endpoint") }}' as endpoint,
    '{{ var("prompt_version") }}' as prompt_version,
    input_chars,
    response.result as result_json,
    length(response.result) as output_chars,
    response.errorMessage as error_message,
    current_timestamp() as extracted_at
from called
