import json
from typing import List
from terno.llm.base import LLMFactory
from terno.models import Organisation


class DBSchema:
    def __init__(self, database_name: str):
        self.name = "DBSchema"
        self.database_name = database_name

    def execute(self, tool_input: dict) -> str:
        """Simulates retrieving the database schema."""
        # In a real implementation, you would connect to the database here
        # and retrieve the schema.  For this example, we'll return a mock schema.
        print(f"DBSchema called with: {tool_input}")
        mock_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "user_id", "type": "INTEGER", "primary_key": True},
                        {"name": "name", "type": "TEXT"},
                        {"name": "location", "type": "TEXT"},
                    ],
                },
                {
                    "name": "sales",
                    "columns": [
                        {"name": "sale_id", "type": "INTEGER", "primary_key": True},
                        {"name": "user_id", "type": "INTEGER", "foreign_key": "users.user_id"},
                        {"name": "product_id", "type": "INTEGER"},
                        {"name": "amount", "type": "REAL"},
                        {"name": "sale_date", "type": "TEXT"},
                    ],
                },
            ],
        }
        return json.dumps(mock_schema)


class GenerateSQL:
    def __init__(self):
        self.name = "GenerateSQL"

    def execute(self, tool_input: dict) -> str:
        """Simulates generating an SQL query."""
        # In a real implementation, you would use an LLM or a more sophisticated
        # method to generate the SQL query based on the user's question
        # and the database schema.
        print(f"GenerateSQL called with: {tool_input}")
        user_question = tool_input.get("question", "")
        if "schema" in tool_input and "canada" in user_question.lower():
            sql_query = """
            SELECT
                u.name,
                s.sale_date,
                s.amount
            FROM
                users u
            JOIN
                sales s ON u.user_id = s.user_id
            WHERE
                u.location = 'Canada';
            """
            return sql_query
        elif "schema" in tool_input:
            sql_query = "SELECT * FROM sales LIMIT 5;" # default query
            return sql_query
        else:
            return "SELECT 'No SQL query can be generated'"


class ExecuteSQL:
    def __init__(self, database_name: str):
        self.name = "ExecuteSQL"
        self.database_name = database_name

    def execute(self, tool_input: dict) -> str:
        """Simulates executing an SQL query against a database."""
        # In a real implementation, you would connect to the database here
        # and execute the query. For this example, we'll return mock results.
        print(f"ExecuteSQL called with: {tool_input}")
        sql_query = tool_input.get("sql", "")
        if "Canada" in sql_query:
            mock_results = [
                {"name": "Alice", "sale_date": "2024-01-15", "amount": 100.00},
                {"name": "Bob", "sale_date": "2024-02-20", "amount": 200.00},
            ]
            return json.dumps(mock_results)
        elif "SELECT * FROM sales LIMIT 5" in sql_query:
             mock_results = [
                {"sale_id": 1, "user_id": 1, "product_id": 101, "amount": 50.00, "sale_date": "2024-03-01"},
                {"sale_id": 2, "user_id": 2, "product_id": 102, "amount": 75.00, "sale_date": "2024-03-05"},
                {"sale_id": 3, "user_id": 1, "product_id": 103, "amount": 120.00, "sale_date": "2024-03-10"},
                {"sale_id": 4, "user_id": 3, "product_id": 101, "amount": 60.00, "sale_date": "2024-03-12"},
                {"sale_id": 5, "user_id": 2, "product_id": 104, "amount": 90.00, "sale_date": "2024-03-15"},
            ]
             return json.dumps(mock_results)
        else:
            return "[]"  # Return an empty list as a JSON string


class Agent:
    def __init__(self, llm=None, database: str = None):
        self.name = 'Database Query Agent'
        self.description = 'An agent that can study a database and answer questions by generating and executing SQL queries.'
        self.system_prompt = """
            You are a helpful agent that can answer questions about a database.
            You have access to the following tools:
            - DBSchema: Retrieves the schema of the database.
            - GenerateSQL: Generates SQL queries.
            - ExecuteSQL: Executes SQL queries and returns the results.
            Use the tools to gather information needed to answer the user's question.
            Do not make assumptions about the database schema; use the DBSchema tool to discover it.
            Respond to the user in a conversational manner.
            """
        llm, is_default_llm = LLMFactory.create_llm(Organisation.objects.first())
        self.llm = llm
        self.memory: List[str] = []
        self.state = 'IDLE'
        self.tools = [DBSchema(database=database), GenerateSQL(), ExecuteSQL(database=database)]
        self.max_steps = 5
        self.current_step = 0
        self.next_step_prompt: str = ''

    def run(self, request: str) -> str:
        self.memory.append(f"User: {request}")
        self.state = 'RUNNING'
        results: List[str] = []
        while self.state != 'FINISHED' and self.current_step < self.max_steps:
            self.current_step += 1
            print(f"\n--- Step {self.current_step} ---")
            step_result = self.step()
            results.append(step_result)
            if "Final Answer:" in step_result:
                self.state = 'FINISHED'
        if self.state != 'FINISHED':
            results.append(f"Reached max steps ({self.max_steps}).  Unable to provide a final answer.")
        self.state = 'IDLE'
        self.current_step = 0
        return "\n".join(results)

    def step(self) -> str:
        """
        Executes a single step in the agent's workflow: think and act.

        Returns:
            A string describing the result of the step.
        """
        should_act = self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return self.act()

    def think(self) -> bool:
        """
        Processes the current state (memory) and decides the next action using an LLM.

        Returns:
            True if an action should be taken, False otherwise.
        """
        prompt = self.system_prompt + "\n"
        prompt += "\n".join(self.memory)  # Include conversation history
        prompt += f"\n{self.next_step_prompt}\n" #add next step prompt

        print(f"Prompt:\n{prompt}") # Print the prompt sent to the LLM

        try:
            response = self.llm.ask(prompt=prompt)
        except Exception as e:
            error_message = f"LLM call failed: {e}"
            print(error_message)
            self.memory.append(f"Agent: {error_message}")
            return False

        print(f"LLM Response: {response}")  # Print the LLM's raw response
        self.memory.append(f"Agent: {response}") #store the response

        # Determine if an action is needed and what that action is.
        if "Action:" in response:
            action_name = response.split("Action: ")[1].split("\n")[0]
            action_input_str = response.split("Action Input: ")[1].split("\n")[0]
            return True
        elif "Final Answer:" in response:
             return False
        else:
            self.next_step_prompt = response
            return False

    def act(self) -> str:
        """
        Executes the action decided by the think method.

        Returns:
            A string describing the result of the action.
        """
        # Extract action and input from the last LLM response (stored in memory)
        last_response = self.memory[-1]
        action_name = last_response.split("Action: ")[1].split("\n")[0]
        action_input_str = last_response.split("Action Input: ")[1].split("\n")[0]

        action_input = {"question": action_input_str} #default

        if action_name == "GenerateSQL":
            schema_response = next((msg for msg in self.memory if "DBSchema" in msg), None)
            if schema_response:
                schema_data = schema_response.split("Result:")[1]
                action_input = {"question": action_input_str, "schema": schema_data}

        tool = next((t for t in self.tools if t.name == action_name), None)
        if not tool:
            error_message = f"Error: Unknown tool '{action_name}'"
            print(error_message)
            self.memory.append(f"Agent: {error_message}")
            return error_message

        try:
            result = tool.execute(tool_input=action_input)
            print(f"Tool '{action_name}' executed. Result: {result}")
            self.memory.append(f"{tool.name} Result: {result}")
            self.next_step_prompt = result
            return f"{tool.name} Result: {result}"
        except Exception as e:
            error_message = f"Tool '{action_name}' execution failed: {e}"
            print(error_message)
            self.memory.append(f"Agent: {error_message}")
            return error_message
