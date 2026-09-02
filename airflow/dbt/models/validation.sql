{{ config(
    materialized='table',
    alias='validation_' ~ var('source_table')[:50]
) }}

{% set source_table = var('source_table') %}
{% set clean_table = ('clean_' ~ source_table)[:63] %}

{% set raw_relation = adapter.get_relation(
    database=target.database,
    schema='public',
    identifier=source_table
) %}

{% set clean_relation = adapter.get_relation(
    database=target.database,
    schema='public',
    identifier=clean_table
) %}

{% if raw_relation is none %}

SELECT
    '{{ source_table }}' AS source_table,
    0 AS raw_rows,
    0 AS clean_rows,
    0 AS removed_rows,
    0.00 AS retention_rate,
    'FAIL - RAW TABLE NOT FOUND' AS validation_status

{% elif clean_relation is none %}

SELECT
    '{{ source_table }}' AS source_table,
    (SELECT COUNT(*) FROM {{ raw_relation }}) AS raw_rows,
    0 AS clean_rows,
    (SELECT COUNT(*) FROM {{ raw_relation }}) AS removed_rows,
    0.00 AS retention_rate,
    'FAIL - CLEAN TABLE NOT FOUND' AS validation_status

{% else %}

WITH row_count AS (
    SELECT
        (SELECT COUNT(*) FROM {{ raw_relation }}) AS raw_rows,
        (SELECT COUNT(*) FROM {{ clean_relation }}) AS clean_rows
)

SELECT
    '{{ source_table }}' AS source_table,
    raw_rows,
    clean_rows,
    raw_rows - clean_rows AS removed_rows,

    ROUND(
        CASE
            WHEN raw_rows = 0 THEN 0
            ELSE (clean_rows::numeric / raw_rows::numeric) * 100
        END,
        2
    ) AS retention_rate,

    CASE
        WHEN raw_rows = 0 THEN 'FAIL - RAW TABLE EMPTY'
        WHEN clean_rows = 0 THEN 'FAIL - CLEAN TABLE EMPTY'
        WHEN clean_rows > raw_rows THEN 'FAIL - CLEAN ROWS EXCEED RAW'
        ELSE 'PASS'
    END AS validation_status

FROM row_count

{% endif %}