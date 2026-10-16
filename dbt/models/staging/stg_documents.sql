select document_id, pair_id, agency_id, policy_version, path, scanned
from {{ source('raw', 'documents') }}
