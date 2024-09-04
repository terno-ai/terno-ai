from terno.pipeline.abstract_pipeline import AbstractPipeline
import time
import logging

logger = logging.getLogger(__name__)


class Pipeline(AbstractPipeline):
    _steps = []

    def __init__(self, steps):
        self._steps = steps

    def add_step(self, step):
        self._steps.append(step)

    def run(self):
        try:
            result = []
            for step in self._steps:
                start_time = time.time()

                step_result = step.execute()

                execution_time = time.time() - start_time
                result.append([step_result, execution_time])

            return result

        except Exception as e:
            logger.warning(e)
