-- One row per document and field, with the cited page and evidence.
-- Values are cleaned here so both years compare on the same terms.
with latest as (
    select *
    from {{ ref('int_extraction_raw') }}
    where error_message is null
      and prompt_version = '{{ var("prompt_version") }}'
    -- keep only the newest extraction per document
    qualify row_number() over (partition by document_id order by extracted_at desc) = 1
),

fields as (
    select
        l.document_id,
        l.agency_id,
        f.field,
        get_json_object(l.result_json, concat('$.', f.field, '.value')) as raw_value,
        try_cast(get_json_object(l.result_json, concat('$.', f.field, '.page')) as int) as page,
        get_json_object(l.result_json, concat('$.', f.field, '.evidence')) as evidence
    from latest l
    lateral view explode(array(
        'policy_number', 'insured_name', 'carrier', 'effective_date', 'vehicle_year', 'vehicle',
        'liability_limit', 'collision_deductible', 'optional_coverages', 'drivers', 'annual_premium'
    )) f as field
),

cleaned as (
    select
        *,
        case
            when raw_value is null or raw_value = 'null' then null
            when field = 'policy_number'
                then upper(regexp_replace(raw_value, '\\s', ''))
            when field in ('insured_name', 'carrier', 'vehicle')
                then trim(regexp_replace(lower(raw_value), '\\s*\\(fictional\\)', ''))
            when field = 'optional_coverages'
                then nullif(array_join(array_sort(array_distinct(from_json(raw_value, 'array<string>'))), ','), '')
            when field = 'annual_premium'
                then format_number(try_cast(regexp_replace(raw_value, '[^0-9.]', '') as decimal(12, 2)), '0.00')
            when field in ('vehicle_year', 'liability_limit', 'collision_deductible', 'drivers')
                then cast(cast(try_cast(regexp_replace(raw_value, '[^0-9.]', '') as double) as bigint) as string)
            when field = 'effective_date' then
                -- OCR sometimes reads the 0 in 2025 as 6 (2625). No policy here starts after 2030,
                -- so put the 0 back when the year is out of range.
                case
                    when try_cast(substring(trim(raw_value), 1, 4) as int) > 2030
                        then concat('20', substring(trim(raw_value), 3))
                    else trim(raw_value)
                end
            else trim(raw_value)
        end as value
    from fields
),

-- OCR can garble names and numbers (0 read as O, Q or @, "general" read as "genera!").
-- The agency knows its own policy list, carriers and vehicle models, so we match each value to
-- the closest known one. A match is only accepted when it is close (3 edits or fewer).
candidates as (
    select c.document_id, c.field, a.policy_number as known
    from cleaned c join {{ ref('stg_ams_policies') }} a on a.agency_id = c.agency_id
    where c.field = 'policy_number'
    union all
    select c.document_id, c.field, a.policy_number
    from cleaned c join {{ ref('stg_ams_policies') }} a on a.agency_id = c.agency_id
    where c.field = 'insured_name'
    union all
    select c.document_id, c.field, trim(regexp_replace(lower(r.carrier), '\\s*\\(fictional\\)', ''))
    from cleaned c cross join {{ ref('ref_carriers') }} r
    where c.field = 'carrier'
    union all
    select c.document_id, c.field, lower(r.vehicle)
    from cleaned c cross join {{ ref('ref_vehicles') }} r
    where c.field = 'vehicle'
),

scored as (
    select
        k.document_id,
        k.field,
        k.known,
        case
            when k.field = 'insured_name' then levenshtein(c.value, lower(a.insured_name))
            else levenshtein(replace(c.value, ' ', ''), replace(lower(k.known), ' ', ''))
        end as distance
    from candidates k
    join cleaned c on c.document_id = k.document_id and c.field = k.field
    left join {{ ref('stg_ams_policies') }} a on k.field = 'insured_name' and a.policy_number = k.known
),

best as (
    select document_id, field, known, distance
    from (
        select *, row_number() over (partition by document_id, field order by distance) as rn
        from scored
    )
    where rn = 1 and distance <= 3
),

-- If the policy number itself is too garbled, fall back to the policy that belongs to the
-- insured named on the document.
policy_fix as (
    select
        d.document_id,
        coalesce(p.known, n.known) as policy_number,
        case when p.known is not null then p.distance else n.distance + 100 end as repair_distance
    from (select distinct document_id from cleaned) d
    left join best p on p.document_id = d.document_id and p.field = 'policy_number'
    left join best n on n.document_id = d.document_id and n.field = 'insured_name'
),

matched as (
    select
        c.document_id, c.agency_id, c.field, c.raw_value, c.page, c.evidence,
        case
            when c.field = 'policy_number' then pf.policy_number
            when c.field in ('carrier', 'vehicle') then coalesce(b.known, c.value)
            -- Same idea for the client name: use the agency record when it is a near match.
            when c.field = 'insured_name' and levenshtein(c.value, lower(am.insured_name)) <= 3
                then lower(am.insured_name)
            else c.value
        end as value,
        case
            when c.field = 'policy_number' then pf.repair_distance
            when c.field in ('carrier', 'vehicle') then b.distance
        end as repair_distance
    from cleaned c
    left join policy_fix pf on pf.document_id = c.document_id
    left join best b on b.document_id = c.document_id and b.field = c.field
    left join {{ ref('stg_ams_policies') }} am on am.policy_number = pf.policy_number
)

select
    c.document_id,
    c.agency_id,
    c.field,
    c.raw_value,
    c.value,
    c.page,
    c.evidence,
    c.repair_distance,
    p.text_method,
    -- For OCR pages: the lowest OCR confidence of any number quoted in the evidence.
    case when p.text_method = 'ocr' then
        array_min(transform(
            filter(
                from_json(p.digit_words, 'array<struct<word:string,conf:double>>'),
                w -> contains(c.evidence, w.word)
            ),
            w -> w.conf
        ))
    end as ocr_confidence,
    -- Traceability: does the quoted evidence really appear on the cited page?
    p.text is not null as cited_page_exists,
    coalesce(
        contains(
            lower(regexp_replace(p.text, '\\s+', ' ')),
            lower(regexp_replace(c.evidence, '\\s+', ' '))
        ),
        false
    ) as evidence_on_page
from matched c
left join {{ ref('stg_document_pages') }} p
    on p.document_id = c.document_id and p.page = c.page
