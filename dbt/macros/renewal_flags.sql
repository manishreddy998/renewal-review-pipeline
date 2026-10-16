{#- The same rules are used for extracted values and for the answer key, so the
    evaluation compares like with like. p is last year, r is the renewal. -#}
{% macro renewal_flags(p, r) %}
    round(({{ r }}.annual_premium - {{ p }}.annual_premium) / nullif({{ p }}.annual_premium, 0) * 100, 1)
        as premium_change_pct,
    ({{ r }}.annual_premium - {{ p }}.annual_premium) / nullif({{ p }}.annual_premium, 0) > 0.15
        as flag_large_premium_increase,
    ({{ r }}.annual_premium - {{ p }}.annual_premium) / nullif({{ p }}.annual_premium, 0) > 0.05
        and ({{ r }}.annual_premium - {{ p }}.annual_premium) / nullif({{ p }}.annual_premium, 0) <= 0.15
        as flag_premium_increase,
    {{ r }}.collision_deductible > {{ p }}.collision_deductible as flag_deductible_raised,
    {{ r }}.liability_limit < {{ p }}.liability_limit as flag_liability_lowered,
    size(array_except(split(coalesce({{ p }}.optional_coverages, ''), ','), split(coalesce({{ r }}.optional_coverages, ''), ','))) > 0
        as flag_coverage_dropped,
    {{ r }}.drivers > {{ p }}.drivers as flag_driver_added,
    ({{ r }}.vehicle != {{ p }}.vehicle or {{ r }}.vehicle_year != {{ p }}.vehicle_year) as flag_vehicle_changed,
    {{ r }}.carrier != {{ p }}.carrier as flag_carrier_changed
{% endmacro %}

{% macro flag_names() %}
    {{ return(['large_premium_increase', 'premium_increase', 'deductible_raised', 'liability_lowered',
               'coverage_dropped', 'driver_added', 'vehicle_changed', 'carrier_changed']) }}
{% endmacro %}

{#- Weights reflect how much a broker would want to see the account. Losing coverage or
    liability limit can leave a client exposed, so those weigh the most. -#}
{% macro flag_weights() %}
    {{ return({'large_premium_increase': 3, 'premium_increase': 1, 'deductible_raised': 2,
               'liability_lowered': 4, 'coverage_dropped': 4, 'driver_added': 1,
               'vehicle_changed': 1, 'carrier_changed': 2}) }}
{% endmacro %}
