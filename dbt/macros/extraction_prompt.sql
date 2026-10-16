{% macro extraction_prompt() -%}
'You read one automobile insurance declarations document from an Ontario broker. The text below
comes from PDF pages, some read by OCR, so it can contain small character errors. Each page starts
with a line like === PAGE n ===.

Return only a JSON object with these keys:
policy_number, insured_name, carrier, effective_date, vehicle_year, vehicle,
liability_limit, collision_deductible, optional_coverages, drivers, annual_premium.

Each key maps to an object {"value": ..., "page": n, "evidence": "..."} where:
- value is the field value, or null if the document does not state it
- page is the page number where you found it
- evidence is the shortest exact piece of text from that page that shows the value

Rules for values:
- effective_date as YYYY-MM-DD
- vehicle_year, liability_limit, collision_deductible, drivers as whole numbers
- annual_premium as a number with two decimals, no currency sign
- vehicle as make and model in normal case, without the year, for example "Toyota RAV4"
- carrier and insured_name exactly as written, in normal case
- optional_coverages as a list using only these codes: collision_or_upset, comprehensive,
  specified_perils, all_perils. How to decide:
  * If the document marks coverages as INCLUDED, list only those. If such a schedule marks no
    coverage as INCLUDED, the list is empty.
  * Otherwise, a line in the coverages section that names a coverage with its own deductible,
    such as "Comprehensive Deductible $500", means that coverage is included.
  * A line marked "if added" never means the coverage is included.
  * A bare COLLISION DEDUCTIBLE line in a schedule that marks other coverages INCLUDED does not
    mean collision is included.
- collision_deductible is the collision deductible amount. Report it even when it is shown
  "if added" and collision coverage itself is not included.
- If OCR clearly garbled a number (for example 1000000.90 next to a limit), give the most likely
  intended value.

Document:
'
{%- endmacro %}
