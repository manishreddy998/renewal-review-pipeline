-- One row per policy version (prior or renewal). All rows are synthetic test data.
select
    pair_id,
    agency_id,
    policy_version,
    policy_number,
    insured_name,
    vehicle_year,
    liability_limit,
    collision_deductible,
    optional_coverages,
    drivers,
    annual_premium,
    planted_changes,
    stamp
from {{ source('raw', 'policy_pairs') }}
