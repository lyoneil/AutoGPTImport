from logging import Logger
from autogpt.core.prompting.base import (
    BasePromptStrategy,
    PromptStrategiesConfiguration,
)
from autogpt.core.agents.usercontext.strategies.refine_user_context import (
    RefineUserContextStrategy,
    RefineUserContextConfiguration,
    RefineUserContextFunctionNames,
)

class StrategiesSetConfiguration(PromptStrategiesConfiguration):
    refine_user_context: RefineUserContextConfiguration


class StrategiesSet:
    from autogpt.core.prompting.base import BasePromptStrategy, PromptStrategy

    @staticmethod
    def get_strategies(logger=Logger) -> list[BasePromptStrategy]:
        return [
            RefineUserContextStrategy(
                logger=logger, **RefineUserContextStrategy.default_configuration.dict()
            ),
        ]
