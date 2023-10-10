from typing import List, Type, Tuple

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Mount
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Select, Button, Placeholder

from screens.frontend_simple import FrontendBase
from templates.template_chat import TemplateChat
from templates.template_default import TemplateBase

# Esto debería calcularse on the fly.
# name -> class reference
TEMPLATES: List[Tuple[str, Type[TemplateBase]]] = [
    ("Base Template", TemplateBase),
    ("Chat Template", TemplateChat),
]


# Esto no carga referencias a nada, las calcula on the fly, pero informa a la app.
class LayoutModal(ModalScreen):
    # Esto emite las clases no las instancias.
    class LayoutChanged(Message):
        def __init__(self, template: Type[TemplateBase], frontend: Type[FrontendBase]):
            self.template = template
            self.frontend = frontend
            super().__init__()

    # Disabled ok y frontend hasta que se elija un elemento template.
    def compose(self) -> ComposeResult:
        yield Grid(
            Select(options=TEMPLATES, prompt='Select a template', id="select-layout-template"),
            Select(options=[], prompt='Template frontend', disabled=True, id="select-layout-frontend"),
            Placeholder(),
            Button("Cancel", variant="error", id="button-layout-cancel"),
            Button("Accept", disabled=True, variant="primary", id="button-layout-accept"),
            id='grid-layout'
        )

    @on(Mount)
    def create_modal(self):
        self.query_one(Grid).border_title = "Configure Layout"

    @on(Button.Pressed, selector='#button-layout-cancel')
    def handle_button_cancel(self, _event: Button.Pressed):
        self.app.pop_screen()

    @on(Button.Pressed, selector='#button-layout-accept')
    def handle_button_accept(self, _event: Button.Pressed):
        template_class: Type[TemplateBase] = self.query_one('#select-layout-template', expect_type=Select).value
        frontend_class: Type[FrontendBase] = self.query_one('#select-layout-frontend', expect_type=Select).value
        self.post_message(LayoutModal.LayoutChanged(template=template_class, frontend=frontend_class))

    # Se cambió de template
    @on(Select.Changed, selector='#select-layout-template')
    def handle_select_template(self, event: Select.Changed):
        # Prepare variables.
        select_frontends: Select = self.query_one(selector='#select-layout-frontend', expect_type=Select)
        button_accept: Button = self.query_one(selector='#button-layout-accept', expect_type=Button)
        # Disable button because changing template means no frontend is chosen.
        button_accept.disabled = True
        if event.value:  # Valid template, populate frontend values.
            # Ya que lo vamos a editar hay que evitar que mande eventos al pedo
            with select_frontends.prevent(Select.Changed):
                template_class: TemplateBase = event.select.value
                select_frontends.set_options(template_class.AVAILABLE_FRONTENDS)
            # Por ultimo habilitarlo.
            select_frontends.disabled = False
        else:  # Sí se elige nada, vaciar el select y ponerlo en modo default
            with select_frontends.prevent(Select.Changed):
                select_frontends.set_options([])
                select_frontends.value = None
            select_frontends.disabled = True
            self.app.bind(keys='f2', action='layout_selection', description="Layouts")

    # Escuchar si se usó el desplegable de frontends
    @on(Select.Changed, selector='#select-layout-frontend')
    def handle_select_frontend(self, event: Select.Changed):
        button_accept: Button = self.query_one('#button-layout-accept', expect_type=Button)
        if event.value:  # Habilitar el button si es una option valida.
            button_accept.disabled = False
        else:
            button_accept.disabled = True
            self.app.bind(keys='f2', action='layout_selection', description="Layouts")
