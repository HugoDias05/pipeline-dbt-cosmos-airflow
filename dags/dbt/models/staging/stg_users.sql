{{ config(materialized='table') }}

with source_data as (
    select
        id,
        first_name,
        last_name,
        email,
        gender,
        ip_address
    from {{ source('raw', 'users') }}
)

select
    id,
    first_name,
    last_name,
    email,
    gender,
    ip_address
from source_data
