#coding=utf8
import re
from dataclasses import dataclass, field
from typing import Optional, Any, Union, List, Dict
from abc import ABC

def remove_quote(text: str) -> str:
    """ 
    If the text is wrapped by a pair of quote symbols, remove them.
    In the middle of the text, the same quote symbol should remove the '/' escape character.
    """
    for quote in ['"', "'", "`"]:
        if text.startswith(quote) and text.endswith(quote):
            text = text[1:-1]
            text = text.replace(f"\\{quote}", quote)
            break
    return text.strip()


@dataclass
class Action(ABC):
    
    action_type: str = field(
        repr=False,
        metadata={"help": 'type of action, e.g. "exec_code", "create_file", "terminate"'}
    )


    @classmethod
    def get_action_description(cls) -> str:
        return """
Action: action format
Description: detailed definition of this action type.
Usage: example cases
Observation: the observation space of this action type.
"""

    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Any]:
        raise NotImplementedError

@dataclass
class EXECUTE_SQL(Action):

    action_type: str = field(default="execute_sql",init=False,repr=False,metadata={"help": 'type of action, c.f., "execute_sql"'})
    sql_query: str = field(metadata={"help": 'SQL query to execute'})
    @classmethod
    def get_action_description(cls) -> str:
        return """
## EXECUTE SQL Action
* Signature: EXECUTE_SQL(sql_query="sql_command")
* Description: Executes an SQL command and the results are displayed in CSV format.
* Examples:
  - Example1: EXECUTE_SQL(sql_query="SELECT * FROM users")
"""
    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'EXECUTE_SQL\(sql_query=(.*?)\)', text, flags=re.DOTALL)
        if matches:
            command = matches[0].strip()
            return cls(sql_query=remove_quote(command))
        return None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sql_query="{self.sql_query}")'
    
@dataclass
class GET_TABLES(Action):

    action_type: str = field(default="get_tables",init=False,repr=False,metadata={"help": 'type of action, c.f., "get_tables"'})

    @classmethod
    def get_action_description(cls) -> str:
        return """
## GET_TABLES Action
* Signature: GET_TABLES()
* Description: Fetch all table names from the database. The results are results are displayed in CSV File format.
* Examples:
  - Example1: GET_TABLES()
"""
    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'GET_TABLES\(\)', text, flags=re.DOTALL)
        if matches:
            return cls()
        return None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

@dataclass
class GET_TABLE_INFO(Action):

    action_type: str = field(default="get_table_info",init=False,repr=False,metadata={"help": 'type of action, c.f., "get_table_info"'})
    table: str = field(metadata={"help": 'Name of the table to fetch information from'})

    @classmethod
    def get_action_description(cls) -> str:
        return """
## GET_TABLE_INFO Action
* Signature: GET_TABLE_INFO(table="table_name")
* Description: Executes a query to fetch all column information (field name, data type, and description) from the specified table in the database.
* Examples:
  - Example1: GET_TABLE_INFO(table="BANK_FOR_INTERNATIONAL_SETTLEMENTS_TIMESERIES")
"""
    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'GET_TABLE_INFO\(table=(.*?)', text, flags=re.DOTALL)
        if matches:
            table = matches[0].strip()
            return cls(table=remove_quote(table))
        return None
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(table="{self.table}")'

@dataclass
class SAMPLE_ROWS(Action):

    action_type: str = field(default="sample_rows",init=False,repr=False,metadata={"help": 'type of action, c.f., "bq_sample_rows"'})

    table: str = field(metadata={"help": 'Name of the table to sample data from'})

    row_number: int = field(metadata={"help": 'Number of rows to sample'})

    @classmethod
    def get_action_description(cls) -> str:
        return """
## SAMPLE_ROWS Action
* Signature: SAMPLE_ROWS(table="table_name", row_number=3)
* Description: Executes a query to sample a specified number of rows from a table. The results are displayed in JSON format.
* Examples:
  - Example1: SAMPLE_ROWS(table="shakespeare", row_number=3)
"""
    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'SAMPLE_ROWS\(table=(.*?), row_number=(.*?)\)', text, flags=re.DOTALL)
        if matches:
            table, row_number = (item.strip() for item in matches[-1])
            return cls(table=remove_quote(table), row_number=int(row_number))
        return None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(table="{self.table}", row_number={self.row_number})'

@dataclass
class SEMANTIC_SEARCH_TABLE(Action):

    action_type: str = field(default="semantic_search_table",init=False,repr=False,metadata={"help": 'type of action, c.f., "bq_sample_rows"'})

    table: str = field(metadata={"help": 'Name of the table to search for a text from'})
    column: str = field(metadata={"help": 'Name of the column to search for a text from'})
    value: str = field(metadata={"help": 'value to search for'})

    row_number: int = field(metadata={"help": 'Number of best matching rows to fetch'})

    @classmethod
    def get_action_description(cls) -> str:
        return """
## SEMANTIC_SEARCH_TABLE Action
* Signature: SEMANTIC_SEARCH_TABLE(table="table_name", column="column_name", value="value to search for", row_number=3)
* Description: It searches for an value in a column in a table and lists the top matching rows from the table in JSON format. If a column has text, use this instead of using the 'like' from SQL to find the rows matching a particular text.
* Examples:
  - Example1: SEMANTIC_SEARCH_TABLE(table="courses", column="title", value="Data Science 2024 Batch 1", row_number=3)
"""
    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'SEMANTIC_SEARCH_TABLE\(table=(.*?), column=(.*?), value=(.*?), row_number=(.*?)\)', text, flags=re.DOTALL)
        if matches:
            table, column, value, row_number = (item.strip() for item in matches[-1])
            return cls(table=remove_quote(table), column=remove_quote(column), value=remove_quote(value), row_number=int(row_number))
        return None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(table="{self.table}", column={self.column}, value={self.value}, row_number={self.row_number})'


@dataclass
class Terminate(Action):

    action_type: str = field(
        default="terminate",
        init=False,
        repr=False,
        metadata={"help": "terminate action representing the task is finished, or you think it is impossible for you to complete the task"}
    )

    output: Optional[str] = field(
        default=None,
        metadata={"help": "answer to the task or 'FAIL', if exists"}
    )

    code : str = field(
        default=''
    )

    @classmethod
    def get_action_description(cls) -> str:
        return """
## Terminate Action
* Signature: Terminate(output="literal_answer_or_output_path")
* Description: This action denotes the completion of the entire task and returns the final answer. If the answer is a table, it must be displayed in a CSV format. 
* Examples:
  - Example1: Terminate(output="New York")
  - Example2: Terminate(output="FAIL")
"""

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(output="{self.output}")'

    @classmethod
    def parse_action_from_text(cls, text: str) -> Optional[Action]:
        matches = re.findall(r'Terminate\(output=(.*?)\)', text, flags=re.DOTALL)
        if matches:
            output = matches[-1]
            return cls(output=remove_quote(output))
        return None

