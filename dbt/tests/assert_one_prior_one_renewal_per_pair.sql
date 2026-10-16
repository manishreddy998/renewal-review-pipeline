-- Every pair must have exactly one prior and one renewal row.
select pair_id
from {{ ref('stg_policy_pairs') }}
group by pair_id
having count(*) != 2 or count(distinct policy_version) != 2
