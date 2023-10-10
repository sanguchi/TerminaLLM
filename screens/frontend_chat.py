# displays chat style
# uses kwargs to determine class [(class, message), (...)]
from typing import Dict, Any

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Static, Footer

from screens.frontend_simple import FrontendBase


class FrontendChat(FrontendBase):
    def compose(self) -> ComposeResult:
        yield VerticalScroll()
        yield Input(placeholder="Input message...")
        yield Footer()

    # Handle before App to append human message first
    @on(Input.Submitted)
    def handle_input_submitted(self, event: Input.Submitted):
        if event.value:
            message_static: Static = Static(renderable=event.value, classes='human')
            self.query_one(selector=VerticalScroll).mount(message_static)
            message_static.scroll_visible()

    def handle_output(self, output_text: str, **kwargs):
        css_class: str = 'human'
        # kwargs es un diccionario {'class': 'human' | 'model'}
        if kwargs:
            print(kwargs)
            css_class = kwargs['class']
        message_static: Static = Static(renderable=output_text, classes=css_class)
        self.query_one(selector=VerticalScroll).mount(message_static)
        message_static.scroll_visible()

    def handle_error(self):
        pass