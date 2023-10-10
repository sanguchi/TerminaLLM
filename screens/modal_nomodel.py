from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Label, Button


class NoModelScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(renderable="No model Loaded!\nPlease use the Model Selection menu"),
            Button(label="Dismiss", variant="warning"),
            id='nomodel_grid'
        )

    @on(Button.Pressed)
    def dismiss_modal(self, event: Button.Pressed):
        self.app.pop_screen()