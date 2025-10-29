
  
    

    create or replace table `projeto-dbt-476300`.`users_dbt_marts`.`dim_users`
      
    
    

    OPTIONS()
    as (
      

with users as (
    select
        id as user_id,
        first_name,
        last_name,
        email,
        gender,
        ip_address
    from `projeto-dbt-476300`.`users_dbt_staging`.`stg_users`
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
    );
  