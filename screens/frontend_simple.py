from typing import Tuple

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Grid, VerticalScroll
from textual.events import Mount, Key
from textual.screen import Screen, ModalScreen
from textual.widgets import TextArea, Footer, Input, Static, Label, LoadingIndicator, Button, Rule


# Esto trae 3 frontends, el base con un input y un static, el single panel y el dual panel.

class FrontendBase(Screen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder='Input text...')
        yield VerticalScroll()
        yield Footer()

    def handle_output(self, output_text: str, **kwargs):
        new_label = Label(renderable=output_text, markup=False)
        self.query_one(VerticalScroll).mount(Rule(), new_label, before=0)
        # new_label.scroll_visible()


# Todas las screen mandan submitted event, que se maneja en la app
class FrontendDualPanels(Screen):
    BINDINGS = [
        Binding(key='ctrl+enter', action='emit_submit', description='Send to LLM'),
        Binding(key='f5', action='toggle_style', description='Style'),
    ]

    def __init__(self):
        super().__init__()
        self.input_dummy = Input()
        self.textarea_input = TextArea()
        self.static_output = Static(markup=False)

    def compose(self) -> ComposeResult:
        yield Grid(
            self.textarea_input,
            VerticalScroll(
                self.static_output,
            ),
        )
        yield Footer()

    @on(Key)
    async def intercept_newline(self, event: Key):
        if event.key == 'ctrl+j':
            # hack estupido para emular el submit
            # self.input_dummy.value = self.textarea_input.text
            await self.action_emit_submit()

    @on(Mount)
    def setup_textareas(self, event: Mount):
        self.textarea_input.border_title = 'TEXT INPUT'
        self.textarea_input.show_line_numbers = False
        self.query_one(VerticalScroll).border_title = 'MODEL OUTPUT'
        self.mount(self.input_dummy)
        self.input_dummy.styles.display = 'none'

    def action_toggle_style(self):
        # Esta huevada es simple, tomamos el grid 1x2 y lo damos vuelta (2x1) xddd
        grid = self.query_one(Grid)
        rows, columns = grid.styles.grid_size_rows, grid.styles.grid_size_columns
        grid.styles.grid_size_rows, grid.styles.grid_size_columns = columns, rows

    def action_copy_answer(self):
        self.textarea_input.clear()
        self.textarea_input.insert(self.static_output.renderable)

    def handle_output(self, output_text: str, **kwargs):
        self.static_output.update(output_text)

    async def action_emit_submit(self):
        self.input_dummy.value = self.textarea_input.text
        self.post_message(Input.Submitted(self.input_dummy, self.textarea_input.text, None))
        # await self.input_dummy.action_submit()


# Pseudo colaboratory editing.
# Cuando escribo y presiono inferir, se guarda el cursor, se borra y reemplaza el texto y se pone el cursor al final
# If you continue writing while inference, this means original prompt < current text len, then we will paste full
# inference text and add the diff at the end, with the cursor at the end.
# If you delete some text while inference(prompt > textarea), then we will paste the full inference text but retaining
# the cursor position.
class FrontendSinglePanel(Screen):
    BINDINGS = [
        Binding(key='ctrl+enter', action='emit_submit', description='Send to LLM'),
    ]

    def __init__(self):
        super().__init__()
        self.input_dummy = Input()
        self.textarea = TextArea()
        self.last_prompt: str = ""

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            self.textarea,
            self.input_dummy,
        )
        yield Footer()

    @on(Key)
    async def handle_control_enter(self, event: Key):
        if event.key == 'ctrl+j':
            await self.action_emit_submit()

    async def action_emit_submit(self):
        print("ACTION EMIT SUBMIT")
        self.last_prompt = self.textarea.text
        self.input_dummy.value = self.textarea.text
        self.post_message(Input.Submitted(self.input_dummy, self.last_prompt, None))
        print("ACTION EMIT FINISHED")

    def handle_output(self, output_text: str, **kwargs):
        cursor_location: Tuple[int, int] = self.textarea.cursor_location
        current_text: str = self.textarea.text
        self.textarea.clear()
        # Caso normal, el usuario esperó al completado.
        if current_text == self.last_prompt:
            self.textarea.insert(output_text)
        else:
            # User was typing while inference
            if len(current_text) > len(self.last_prompt):
                self.textarea.insert(output_text + current_text[len(self.last_prompt):])
            else:  # User deleted text while inference, recover cursor location.
                self.textarea.insert(output_text)
                self.textarea.move_cursor(cursor_location)
