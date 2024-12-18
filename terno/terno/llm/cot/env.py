from actions import Action, Terminate, EXECUTE_SQL, GET_TABLES, GET_TABLE_INFO, SAMPLE_ROWS, SEMANTIC_SEARCH_TABLE
from utils import *

DEFAULT_TIME_OUT = 200 # default waiting time for each action

class TernoShieldEnv:
    def __init__(self, session):
        self.session = session
    
    def step(self, action: Action):
        try:
            with timeout(DEFAULT_TIME_OUT,"Action execution time exceeded!"):
                done = False
                if isinstance(action, GET_TABLES):
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
        
        observation = self._handle_observation(observation)
        # logger.info("Observation: %s", observation)
        return observation, done
    
    def execute_get_tables(action):
        #TODO: To implement
        pass
    def get_table_info(action):
        #TODO: To implement
        pass
    def execute_sql(action):
        #TODO: To implement
        pass
    def execute_sample_rows(action):
        #TODO: To implement
        pass
    def semantic_search_table(action):
        #TODO: To implement
        pass
    
    def close(self):
        pass