
  
    

    create or replace table `projeto-dbt-476300`.`users_dbt_staging`.`stg_users`
      
    
    

    OPTIONS()
    as (
      

with source_data as (
    select
        id,
        first_name,
        last_name,
        email,
        gender,
        ip_address
    from `projeto-dbt-476300`.`raw`.`users`
)

select
    id,
    first_name,
    last_name,
    email,
    gender,
    ip_address
from source_data
    );
  