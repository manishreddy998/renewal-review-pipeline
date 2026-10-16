select document_id, page, text, text_method, digit_words
from {{ source('raw', 'document_pages') }}
