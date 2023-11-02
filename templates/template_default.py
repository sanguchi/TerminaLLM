from typing import List, Tuple, Type, Dict, Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.events import Mount
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Switch, Label, Select, TextArea, Footer

from screens.frontend_simple import FrontendBase, FrontendDualPanels, FrontendSinglePanel
from screens.modal_nomodel import NoModelScreen


# El App es padre del template y el template contiene al frontend.
# Template configura el procesamiento de texto y el display.
class TemplateBase(Screen):
    BINDINGS = [
        Binding(key='f1', action='loader_settings', description="Loader Settings"),
        Binding(key='f2', action='template_settings', description="Dismiss"),
        Binding(key='f4', action='return_default', description="Return"),
    ]
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
        super().__init__()
        self.frontend = frontend

    # Build settings, de momento el syntax, el return full text y el continuous gen?.
    def compose(self) -> ComposeResult:
        with Grid():
            yield Label(renderable="Return full text")
            yield Switch()
        yield Footer()

    def process_input(self, text_prompt: str) -> str:
        return text_prompt

    def process_output(self, text_output: str) -> Tuple[str, Dict[str, Any]]:
        return text_output, {}

    def action_return_default(self):
        self.app.switch_mode('default')

    def action_template_settings(self):
        self.dismiss()
        # self.app.pop_screen()

    def action_loader_settings(self):
        self.dismiss()
        # self.app.pop_screen()
        if self.app.loader_modal.model:
            self.app.push_screen(self.app.loader_modal.model.settings)
        else:
            self.app.push_screen(NoModelScreen())