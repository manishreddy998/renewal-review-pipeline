-- Policy list exported from the agency management system.
select policy_number, agency_id, insured_name
from {{ source('raw', 'ams_policies') }}
