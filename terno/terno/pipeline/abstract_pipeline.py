from abc import ABC, abstractmethod


class AbstractPipeline(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run(self, input):
        raise NotImplementedError("Run method not implemented")
