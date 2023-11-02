from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.validation import Number, Integer
from textual.widgets import Label, Switch, Footer, Input


class LoaderModel(object):

    # Deberia poner un widget acá?

    def __init__(self, model_dir_path: str, model_file_path: str):
        self.settings = LoaderSettings()

    def loader_inference(self, text_prompt: str, seed: int = -1):
        pass

    def unload_model(self):
        pass


# Realmente no sé si sea buena idea meter la logica de la UI en la logica del modelo, pero bueno.
class LoaderSettings(Screen):
    BINDINGS = [
        Binding(key='f1', action='loader_settings', description="Dismiss"),
        Binding(key='f2', action='template_settings', description="Template Settings"),
        Binding(key='f4', action='return_default', description="Return"),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Horizontal(
                Label("max_new_tokens"),
                Input(value="150", validators=[Integer(minimum=0)]),
            )
        )
        yield Footer()

    def action_return_default(self):
        self.app.switch_mode('default')

    def action_loader_settings(self):
        self.dismiss()

    def action_template_settings(self):
        self.dismiss()
        if self.app.template:
            self.app.push_screen(self.app.template)
        else:
            self.app.action_layout_selection()