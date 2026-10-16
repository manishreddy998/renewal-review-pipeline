{#- Agency isolation in Unity Catalog.
    agency_can_see(principal, agency_id) is true only when the seed agency_access grants that
    principal that agency. The row filter applies it to the current user. Workspace admins
    see everything so the pipeline owner can run checks. -#}
{% macro create_agency_row_filter() %}
    {#- Runs as a post hook of the agency_access seed, so the table exists first. -#}
    {% if target.type == 'databricks' and execute %}
        {% set fq = target.catalog ~ '.' ~ target.schema %}
        {% do run_query('create schema if not exists ' ~ fq) %}
        {% do run_query(
            'create or replace function ' ~ fq ~ '.agency_can_see(p_principal string, p_agency_id string) '
            ~ 'returns boolean return exists (select 1 from ' ~ fq ~ '.agency_access a '
            ~ 'where lower(a.principal) = lower(p_principal) and a.agency_id = p_agency_id)'
        ) %}
        {% do run_query(
            'create or replace function ' ~ fq ~ '.agency_row_filter(agency_id string) '
            ~ 'returns boolean return is_account_group_member(\'admins\') or is_member(\'admins\') '
            ~ 'or ' ~ fq ~ '.agency_can_see(current_user(), agency_id)'
        ) %}
    {% endif %}
{% endmacro %}

{% macro agency_view(agency_id) %}
-- Work list for one agency only. Brokers at this agency get access to this view and nothing else.
select *
from {{ ref('mart_renewal_queue') }}
where agency_id = '{{ agency_id }}'
{% endmacro %}
