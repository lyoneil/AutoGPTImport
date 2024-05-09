import abc

from forge.llm.providers import AssistantChatMessage
from forge.models.config import SystemConfiguration

from .schema import ChatPrompt, LanguageModelClassification


class PromptStrategy(abc.ABC):
    default_configuration: SystemConfiguration

    @property
    @abc.abstractmethod
    def model_classification(self) -> LanguageModelClassification:
        ...

    @abc.abstractmethod
    def build_prompt(self, *_, **kwargs) -> ChatPrompt:
        ...

    @abc.abstractmethod
    def parse_response_content(self, response_content: AssistantChatMessage):
        ...
