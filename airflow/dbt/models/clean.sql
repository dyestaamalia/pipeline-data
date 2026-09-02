{% set source_table = var('source_table') %}

{% set clean_table = ('clean_' ~ source_table)[:63] %}

{{ config(
    materialized='table',
    alias=clean_table
) }}

{% set source_relation = api.Relation.create(
    database=target.database,
    schema='public',
    identifier=source_table,
    type='table'
) %}

SELECT DISTINCT
    {{ clean_columns(source_relation) }}

FROM {{ source_relation }}