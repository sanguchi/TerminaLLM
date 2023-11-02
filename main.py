from typing import Dict, Tuple

from textual import on, work
from textual.app import App
from textual.binding import Binding
from textual.events import Mount
from textual.widgets import Input
from textual.widgets._select import SelectCurrent

from loaders.loader_generic import LoaderModel, LoaderSettings
from screens.frontend_simple import FrontendBase
from screens.modal_layout import LayoutModal
from screens.modal_loader import LoaderModal
from screens.modal_nomodel import NoModelScreen
from screens.settings_global import GlobalSettings
from templates.template_default import TemplateBase


class FrontendApp(App):
    CSS_PATH = 'styles.tcss'

    BINDINGS = [
        Binding(key='f1', action='model_selection', description="Models"),
        Binding(key='f2', action='layout_selection', description="Layouts"),
        Binding(key='f3', action='custom_screen', description="?????"),
        Binding(key='f4', action='settings_screen', description="Settings"),
    ]

    MODES = {
        'default': FrontendBase,
        'settings': GlobalSettings,
    }

    def __init__(self, driver_class=None, css_path=None, watch_css=False):
        super().__init__(driver_class, css_path, watch_css)
        self.template = TemplateBase()
        self.frontend = self.template.DEFAULT_FRONTEND()
        self.loader_modal = LoaderModal()
        self.layout_modal = LayoutModal()

    # 3 modals 1 screen
    @on(Mount)
    def organize_screens(self):
        # Instalar los modales porque van y vienen
        self.install_screen(screen=self.loader_modal, name='modal_loader')
        self.install_screen(screen=self.layout_modal, name='modal_layout')
        # Instalar el template settings
        self.install_screen(screen=self.template, name='settings_template')
        # El frontend es permanente mientras no lo cambien
        self.switch_mode('default')
        self.push_screen(self.frontend)

    def action_model_selection(self):
        self.push_screen(screen='modal_loader')

    def action_layout_selection(self):
        # Regresar el modal con el estado de los selects.
        self.push_screen(screen='modal_layout')

    def action_settings_screen(self):
        self.switch_mode('settings')

    @on(Input.Submitted)
    def submit_prompt(self, event: Input.Submitted):
        print("SUBMIT FROM FRONTEND")
        if not event.value:
            return
        if self.loader_modal.model:
            event.input.value = ''
            # Configurar boolean para correr en un thread aparte.
            # Los templates podrían deshabilitarlo?
            processed_prompt: str = self.template.process_input(event.value)
            self.run_inference(processed_prompt)
        else:
            # Push no model message | Alert no model.
            self.push_screen(NoModelScreen())

    @on(LayoutModal.LayoutChanged)  # Recordar que event solo tiene referencias a CLASES no instancias
    def handle_layout_changed(self, event: LayoutModal.LayoutChanged):
        # Crear las instancias nuevas
        new_template: TemplateBase = event.template()
        new_frontend: FrontendBase = event.frontend()
        old_template: TemplateBase = self.template
        # Operaciones en el MODE default
        # DEFAULT STACK: [0] old frontend -> [1]modal_layout
        self.pop_screen()  # Quitar el modal
        # DEFAULT STACK: [0] old frontend
        # Update app references
        self.template: TemplateBase = new_template
        self.frontend: FrontendBase = new_frontend
        self.switch_screen(screen=self.frontend)  # Cambiar el frontend.
        # Update footer label
        frontend_name: str = self.layout_modal.query_one('#select-layout-frontend SelectCurrent', SelectCurrent).label
        self.bind(keys='f2', action='layout_selection', description=frontend_name)
        # Operaciones en el MODE settings
        # SETTINGS STACK: [0] app settings -> (optional)[1] template settings OR loader settings
        # actualizar template settings
        self.switch_mode(mode='settings')  # Ir al modo settings y fijarse si está en uso
        if len(self.screen_stack) > 1:  # El stack tiene [1] y no sabemos que settings es de los dos.
            if isinstance(self.screen, type(old_template)):  # Confirmado, es un template settings
                self.pop_screen()  # Quitar template settings del stack para poder reinstalar.
        # Reinstalacion del template settings screen
        self.uninstall_screen(screen='settings_template')
        self.install_screen(screen=self.template, name='settings_template')
        # Go back to default mode
        self.switch_mode(mode='default')

    @on(LoaderModal.ModelChanged)
    def handle_model_changed(self, event: LoaderModal.ModelChanged):
        self.bind(keys='f1', action='model_selection', description=event.model_name[:10])
        # MODE settings ->
        self.switch_mode(mode='settings')
        if len(self.screen_stack) > 1:
            if isinstance(self.screen, LoaderSettings):
                self.pop_screen()
        self.uninstall_screen(screen='settings_model')
        self.install_screen(screen=event.model_loader.settings, name='settings_model')
        self.switch_mode(mode='default')

    @work(exclusive=True, thread=True)
    async def run_inference(self, prompt_text: str):
        # Uso un thread para no congelar la interfaz
        response: str = self.loader_modal.model.loader_inference(prompt_text)
        processed_response: Tuple[str, Dict] = self.template.process_output(response)
        self.frontend.handle_output(processed_response[0], **processed_response[1])


if __name__ == "__main__":
    app = FrontendApp()
    app.run()
