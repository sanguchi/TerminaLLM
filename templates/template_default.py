from typing import List, Tuple, Type, Dict, Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Mount
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Switch, Label, Select, TextArea

from screens.frontend_simple import FrontendBase, FrontendDualPanels, FrontendSinglePanel


# El App es padre del template y el template contiene al frontend.
# Template configura el procesamiento de texto y el display.
class TemplateBase(Screen):
    class FrontendChanged(Message):
        def __init__(self, frontend: FrontendBase):
            self.frontend = frontend
    # name -> class reference
    AVAILABLE_FRONTENDS: List[Tuple[str, Type[FrontendBase]]] = [
        ('Input and Log', FrontendBase),
        ('Single Panel', FrontendSinglePanel),
        ('Dual Panels', FrontendDualPanels),
    ]
    # default class
    DEFAULT_FRONTEND: Type[FrontendBase] = FrontendBase

    def __init__(self, frontend: FrontendBase = DEFAULT_FRONTEND()):
        self.frontend = frontend

    # Build settings, de momento el syntax, el return full text y el continuous gen?.
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(renderable='Return Full Text'),
            Switch(),
            # Label(renderable='Syntax Hightlighting'),
            # Select(options=self.SYNTAX_HIGHLIGHTING, prompt='None'),
        )

    @on(Mount)
    def mount_frontend(self):
        pass

    def process_input(self, text_prompt: str) -> str:
        return text_prompt

    def process_output(self, text_output: str) -> Tuple[str, Dict[str, Any]]:
        return text_output, {}
