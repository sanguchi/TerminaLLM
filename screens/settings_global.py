from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Label, Switch, Footer

from screens.modal_nomodel import NoModelScreen
# from main import FrontendApp
from templates.template_default import TemplateBase


class BaseSettings(Screen):
    pass


class GlobalSettings(BaseSettings):
    BINDINGS = [
        Binding(key='f1', action='loader_settings', description="Loader Settings"),
        Binding(key='f2', action='template_settings', description="Template Settings"),
        Binding(key='f4', action='return_default', description="Return"),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Horizontal(
                Label("Dark Mode"),
                Switch(value=True),
            )
        )
        yield Footer()

    @on(Switch.Changed)
    def change_theme(self, event: Switch.Changed):
        self.app.dark = event.value
        # Reload frontend?
        # self.app.template = TemplateBase()
        # self.app.frontend = self.app.template.DEFAULT_FRONTEND()

    def action_return_default(self):
        self.app.switch_mode('default')

    def action_loader_settings(self):
        if self.app.loader_modal.model:
            self.app.push_screen(self.app.loader_modal.model.settings)
        else:
            self.app.push_screen(NoModelScreen())

    def action_template_settings(self):
        if self.app.is_screen_installed(screen='settings_template'):
            self.app.push_screen(screen='settings_template')
        # if self.app.template:
            # self.app.push_screen(self.app.template)
        else:
            self.app.action_layout_selection()