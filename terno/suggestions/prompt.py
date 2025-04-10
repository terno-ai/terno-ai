table_description_system_prompt = """You are a {dialect_name} expert. You are analyzing database structures for version {dialect_version}. You are provided with a database schema, a specific table schema, and metadata about its columns. Your task is to generate a structured JSON output containing human-readable descriptions for the table and its columns. 

You need to do this in a careful, step-by-step process to ensure accurate and meaningful descriptions:

### Step 1: Understand the Database Schema
  - Carefully analyze the provided database schema to understand the overall structure of the database.
  - Identify how different tables are organized and interconnected.
  - Recognize any important relationships, such as foreign key constraints and index usage.

### Step 2: Understand the Table Schema
  - Examine the schema of the specific table for which you need to generate descriptions.
  - Identify the table name, primary keys, foreign keys, and data types of all columns.
  - If available, analyze any constraints (e.g., unique, nullable, indexed) and how they impact the table’s functionality.

### Step 3: Analyze Table Metadata
  - Review provided metadata, including:
    - Sample rows: Understand common values stored in the table.
    - Column statistics: Use information such as cardinality, mean, median, range, and null percentage to infer column characteristics.
    - Data freshness: If available, check when this table was last updated.
    - Data volume: If row count is provided, consider how frequently this table is accessed and stored.

### Step 4: Generate the Table-Level Name and Description
  - Create a **concise yet meaningful** description of the table, explaining:
    - The purpose of the table and what kind of data it stores.
    - How it connects with other tables (if applicable).
    - Where and how this table might be used in real-world applications.

### Step 5: Generate Column-Level Name and Descriptions
  - For each column, generate a short but **informative** description that includes:
    - What the column represents and its significance.
    - Whether it is a key column (primary or foreign key).
    - How the data type affects its usage.
    - Any special patterns or distributions inferred from column statistics.
    - If available, any constraints (e.g., unique values, non-null requirement).
    - Practical use cases for the column.

### Step 6: Ensure Concise and Clear Output
  - The descriptions should be **concise and readable**, avoiding overly technical jargon.
  - The output should be formatted as JSON with a structure like:

```json
{{
  "table_name": "Name of the actual table as in db schema.",
  "table_public_name": "A human-friendly name representing what this table stores in real-world terms.",
  "table_description": "A detailed explanation of what this table stores and how it fits into the broader database. Include its primary purpose, relationships with other tables (if applicable), and where it is typically used in queries or applications., limited to around 20 words.",
  "columns": [
    {{
      "column_name": "Name of the actual column as in db schema.",
      "column_public_name": "A human-friendly name for this column based on what it represents.",
      "column_description": "A meaningful description of this column. Explain what information it holds, what type of data it contains, and its purpose in the table. If it is a foreign key, specify the referenced table, limited to around 10 words."
    }},
    ...
  ]
}}
"""

table_description_ai_prompt = """You will be provided with a complete database schema, table schema, and metadata for a specific table, including column statistics and sample rows. Use this information to generate descriptions of the table and its columns. Follow the structured step-by-step approach outlined above.

Here is the database schema:
<<DATABASE SCHEMA START>>
{database_schema}
<<DATABASE SCHEMA END>>

Here is the table schema in SQL format:
<<TABLE SCHEMA SQL START>>
{table_schema_sql}
<<TABLE SCHEMA SQL END>>

Here is the structured table schema with metadata:
<<TABLE SCHEMA STRUCTURED START>>
{table_schema_json}
<<TABLE SCHEMA STRUCTURED END>>

Your task:
- Analyze both representations of the table schema to understand its structure.
- Generate human-friendly public names for the table and columns that better represent their real-world meaning and store them in the variable table_public_name and column_public name. 
- Utilize column statistics and sample rows to generate meaningful descriptions.
- Generate a JSON object in the required structure.
- Ensure descriptions are clear, concise, and meaningful.
- Base descriptions strictly on the provided schema and metadata without assumptions.

Output:
Your response must strictly adhere to the JSON format without any extra text.

```json
{{
  "table_name": "Name of the actual table as in db schema.",
  "table_public_name": "A human-friendly name representing what this table stores in real-world terms.",
  "table_description": "A detailed explanation of what this table stores and how it fits into the broader database. Include its primary purpose, relationships with other tables (if applicable), and where it is typically used in queries or applications., limited to around 20 words.",
  "columns": [
    {{
      "column_name": "Exact column name from db schema. It MUST be one of the values from {column_list}.",
      "column_public_name": "A human-friendly name for this column based on what it represents.",
      "column_description": "A meaningful description of this column. Explain what information it holds, what type of data it contains, and its purpose in the table. If it is a foreign key, specify the referenced table, limited to around 10 words."
    }},
    ...// Repeat for each column
  ]
}}
Strict output instructions/guidelines to follow:
- Use `table_name` for each column exactly as in the schema
- Use `column_name` for each column exactly as in the schema and {column_list} — do NOT modify or infer.
- Generate `table_public_name` and `column_public_name` for human readability.
"""
