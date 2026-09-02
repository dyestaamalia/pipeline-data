{% macro clean_columns(source_relation) %}

    -- dbt processing
    {% set columns = adapter.get_columns_in_relation(source_relation) %}

    -- looping dengan jinja templating
    {% for column in columns %}

        {% set data_type = column.data_type | lower %}

        -- cek tipe data
        {% if data_type in [
            'text',
            'character varying',
            'character',
            'varchar',
            'char',
            'bpchar'
        ] %}

            CASE
                WHEN NULLIF(TRIM({{ column.quoted }}), '') IS NULL
                    THEN NULL

                WHEN UPPER(TRIM({{ column.quoted }})) IN (
                    'NA',
                    'N/A',
                    'NULL',
                    '-'
                )
                    THEN NULL

                ELSE TRIM({{ column.quoted }})
            END AS {{ column.quoted }}

        {% else %}

            {{ column.quoted }}

        {% endif %}

        {% if not loop.last %},{% endif %}

    {% endfor %}

{% endmacro %}