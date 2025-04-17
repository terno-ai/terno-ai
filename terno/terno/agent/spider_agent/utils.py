import signal
import os
import hashlib
import shutil
from typing import Dict
# import pandas as pd
import json
import xml.etree.ElementTree as ET
import yaml
import terno.models as terno_models
import suggestions.utils as suggestions_utils
import terno.utils as terno_utils
import re
from .prompts import LIST_TABLES_PROMPT

TIMEOUT_DURATION = 25

# def is_file_valid(file_path):
#     ext = os.path.splitext(file_path)[1].lower()
#     try:
#         if ext == '.csv':
#             pd.read_csv(file_path)
#         elif ext == '.json':
#             with open(file_path, 'r') as f:
#                 json.load(f)
#         elif ext == '.xml':
#             ET.parse(file_path)
#         elif ext == '.yaml' or ext == '.yml':
#             with open(file_path, 'r') as f:
#                 yaml.safe_load(f)
#         else:
#             return True, None
#         return True, None
#     except Exception as e:
#         return False, str(e)

class timeout:
    def __init__(self, seconds=TIMEOUT_DURATION, error_message="Timeout"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def delete_files_in_folder(folder_path):
    if os.path.exists(folder_path):
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def calculate_sha256(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return hashlib.sha256(file_data).hexdigest()


def infuse_schema_with_descriptions(table_metadata) -> str:
    schema = table_metadata['schema']
    columns_meta = table_metadata['columns']
    sample_rows = table_metadata.get('sample_rows', {})
    col_info = {col['name']: col for col in columns_meta}

    def format_values(col):
        """Format value distribution string if available and description exists."""
        uv = col.get('unique_values', {})
        if not uv or not col.get('description'):
            return ""
        kind = uv.get('unique_value_type')
        values = {k: v for k, v in uv.items() if k != 'unique_value_type'}
        if not values:
            return ""

        if kind == 'top':
            sorted_vals = sorted(values.items(), key=lambda x: -x[1])  # Get all values sorted by their value in descending order
            return " Top values: [" + "; ".join(f"'{k}'" for k, v in sorted_vals) + "]"
        elif kind == 'unique':
            return " Unique values: [" + ", ".join(f"'{k}'" for k in values.keys()) + "]"  # Get all unique keys
        return ""

    def process_line(line):
        col_match = re.match(r'\s*\[([^\]]+)\]\s+([A-Z]+(?:\([^)]+\))?)', line.strip(), re.IGNORECASE)
        if col_match:
            col_name = col_match.group(1)
            if col_name in col_info:
                desc = col_info[col_name].get('description')
                if desc:
                    value_hint = format_values(col_info[col_name])
                    comment = f" -- {desc}{value_hint}"
                    return line.rstrip(',') + comment + ','
        return line

    lines = schema.split('\n')
    infused_lines = [process_line(line) if '[' in line and 'FOREIGN KEY' not in line else line for line in lines]

    if sample_rows:
        sample_rows_comment = "\n\n-- Sample Rows:\n\n"
        sample_rows_comment += "-- " + " | ".join(table_metadata['sample_rows']['column_order']) + "\n"
        sample_rows_data = sample_rows['sample_rows']
        for row in sample_rows_data[:3]:
            sample_rows_comment += "-- " + " | ".join(str(value) for value in row) + "\n"
        infused_lines.append(sample_rows_comment)

    return '\n'.join(infused_lines)


def get_filtered_tables_utils(datasource, user_question):
    # We assume that ignored_tables do not contain table names that user is not permitted to see.
    filtered_tables, ignored_tables = suggestions_utils.get_filtered_tables_demo(datasource.id, user_question)
    tables = terno_models.Table.objects.filter(data_source=datasource, name__in=filtered_tables)
    tables_with_metadata = {}

    mDB = terno_utils.generate_mdb(datasource)
    Mtables = mDB.get_table_dict()

    for table in tables:
        table_info = {'name': table.public_name}

        mtable = Mtables.get(table.name)
        table_info['schema'] = mtable.generate_schema()
        table_info['description'] = table.description

        columns = terno_models.TableColumn.objects.filter(table=table)

        column_data = []
        for col in columns:
            col_info = {'name': col.public_name}
            col_info['description'] = col.description
            col_info['unique_values'] = col.unique_categories

            column_data.append(col_info)

        table_info['columns'] = column_data
        table_info['sample_rows'] = table.sample_rows

        tables_with_metadata[table.name] = table_info

    ignored_tables_with_metadata = dict(
        terno_models.Table.objects
        .filter(data_source=datasource, name__in=ignored_tables)
        .values_list('name', 'description')
    )

    return tables_with_metadata, ignored_tables_with_metadata


def combine_list_tables_prompt_utils(datasource_id, datasource_name, user_question,
                                     ignored_tables_with_metadata, relevant_table_schema):
    filtered_table_schema = "\n\n".join(
        infuse_schema_with_descriptions(schema) 
        for schema in relevant_table_schema.values()
    )
    if ignored_tables_with_metadata:
        list_of_remaining_tables = "\n".join(
            f"{i+1}. {table} -- {desc}" if desc else f"{i+1}. {table}"
            for i, (table, desc) in enumerate(ignored_tables_with_metadata.items())
        )
    else:
        list_of_remaining_tables = "There are no remaining tables as all tables have been already included in the fitere tables schema."

    # Step 4: Fill the prompt template
    final_prompt = LIST_TABLES_PROMPT.format(
        datasource_name=datasource_name,
        datasource_id=datasource_id,
        user_query=user_question,
        list_of_remaining_tables=list_of_remaining_tables,
        filtered_table_schema=filtered_table_schema,
    )

    return final_prompt
