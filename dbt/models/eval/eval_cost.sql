-- Model cost per policy document at list price.
-- Tokens are estimated from characters (about 4 characters per token for English text).
-- DBU rates are from the Databricks proprietary model serving price page for the endpoint used.
with x as (
    select
        document_id,
        agency_id,
        input_chars + {{ var('prompt_chars') }} as input_chars,
        output_chars
    from {{ ref('int_extraction_raw') }}
    where prompt_version = '{{ var("prompt_version") }}'
    qualify row_number() over (partition by document_id order by extracted_at desc) = 1
)

select
    '{{ var("extraction_endpoint") }}' as endpoint,
    count(*) as documents,
    round(avg(input_chars) / 4) as avg_input_tokens,
    round(avg(output_chars) / 4) as avg_output_tokens,
    round(sum(input_chars) / 4 / 1e6 * {{ var('dbu_per_m_input') }}
        + sum(output_chars) / 4 / 1e6 * {{ var('dbu_per_m_output') }}, 4) as total_dbu,
    round((sum(input_chars) / 4 / 1e6 * {{ var('dbu_per_m_input') }}
        + sum(output_chars) / 4 / 1e6 * {{ var('dbu_per_m_output') }}) * {{ var('usd_per_dbu') }}, 4) as total_usd,
    round((sum(input_chars) / 4 / 1e6 * {{ var('dbu_per_m_input') }}
        + sum(output_chars) / 4 / 1e6 * {{ var('dbu_per_m_output') }}) * {{ var('usd_per_dbu') }} / count(*), 6)
        as usd_per_document
from x
