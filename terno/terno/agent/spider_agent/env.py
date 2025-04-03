from .actions import Action, Terminate, EXECUTE_SQL, GET_TABLES, GET_TABLE_INFO, SAMPLE_ROWS, SEMANTIC_SEARCH_TABLE
from .utils import *
import terno.utils as utils

DEFAULT_TIME_OUT = 200 # default waiting time for each action


class TernoShieldEnv:
    def __init__(self, datasource, mDB):
        self.db_type = datasource.type
        self.mDB = mDB

    def step(self, action: Action):
        try:
            # with timeout(DEFAULT_TIME_OUT, "Action execution time exceeded!"):
            done = False
            if isinstance(action, GET_TABLES):
                print('action ---', action)
                observation = self.execute_get_tables(action)
            elif isinstance(action, GET_TABLE_INFO):
                observation = self.get_table_info(action)
            elif isinstance(action, EXECUTE_SQL):
                observation = self.execute_sql(action)
            elif isinstance(action, SAMPLE_ROWS):
                observation = self.execute_sample_rows(action)
            elif isinstance(action, SEMANTIC_SEARCH_TABLE):
                observation = self.semantic_search_table(action)
            elif isinstance(action, Terminate):
                observation = "Terminate"
                done = True
            else:
                raise ValueError(f"Unrecognized action type {action.action_type} !")
        except TimeoutError as e:
            observation = str(e)

        # observation = self._handle_observation(observation)
        # logger.info("Observation: %s", observation)
        return observation, done

    def execute_get_tables(self, action):
        return self.mDB.generate_schema()

    def get_table_info(action):
        return

    def execute_sql(self, action):
        native_sql_response = utils.generate_native_sql(
        self.mDB, user_sql, datasource.dialect_name)

    def execute_sample_rows(action):
        return

    def semantic_search_table(action):
        return

    def close(self):
        pass
