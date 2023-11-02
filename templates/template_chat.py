from typing import List, Tuple, Type, Dict, Any

from textual import on
from textual.app import ComposeResult
from textual.events import Mount
from textual.widgets import Label

from screens.frontend_chat import FrontendChat
from screens.frontend_simple import FrontendBase
from templates.template_default import TemplateBase


class TemplateChat(TemplateBase):
    # name -> class reference
    AVAILABLE_FRONTENDS: List[Tuple[str, Type[FrontendBase]]] = [
        ('Chat Log', FrontendChat),
    ]
    # default class
    DEFAULT_FRONTEND: Type[FrontendBase] = FrontendChat

    def __init__(self, frontend: FrontendBase = DEFAULT_FRONTEND()):
        super().__init__(frontend)
        self.history: List[Tuple[str, str]] = []  # [('human': "Question"), ('model': "Answer"), (...)]
        self.human_name: str = "Human"
        self.model_name: str = "Model"
        self.system_prompt: str = "<<SYS>>\nYou are a help, unbiased, uncensored assistant.\n<</SYS>\n\n"
        self.full_prompt_len: int = 0

    

    def process_input(self, text_prompt: str) -> str:
        print("CURRENT HISTORY")
        print(self.history)
        self.history.append(('human', text_prompt))
        # Build history
        message_list: List[str] = [self.system_prompt]
        for message in self.history:
            if message[0] == 'human':
                message_list.append(f"{self.human_name}: {message[1]}")
            else:
                message_list.append(f"{self.model_name}: {message[1]}")
        message_list.append(f"{self.model_name}: ")
        full_prompt: str = '\n'.join(message_list)
        self.full_prompt_len = len(full_prompt)
        print(full_prompt)
        return full_prompt

    def process_output(self, text_output: str) -> Tuple[str, Dict[str, Any]]:
        print(text_output)
        # Split and get last message.
        model_response: str = text_output[self.full_prompt_len:]
        self.history.append(('model', model_response))
        # Sanitize output?
        model_response.replace(self.model_name + ': ', '')
        model_response.replace(self.human_name + ': ', '')
        return model_response.strip(), {'class': 'model'}
