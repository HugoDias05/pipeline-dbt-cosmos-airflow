{{ config(materialized='table') }}

with users as (
    select
        id as user_id,
        first_name,
        last_name,
        email,
        gender,
        ip_address
    from {{ ref('stg_users') }}
)

select
    user_id,
    first_name,
    last_name,
    email,
    gender,
    ip_address,
    concat(first_name, ' ', last_name) as full_name
from users
