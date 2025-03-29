from abc import ABC
from typing import Optional, Any


class Action(ABC):
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


class GenerateSQL(Action):
    def get_action_description(cls) -> str:
        return """
            Action: Generate SQL using prompt
        """

    def parse_action_from_text(cls) -> str:
        return ""


class ExecuteSQL(Action):
    pass
