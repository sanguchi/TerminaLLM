import os
from typing import Type, List

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Mount
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Select, Button, LoadingIndicator, Placeholder
from textual.worker import Worker

import loaders.loader_generic

# Only append loaders that don't fail to load
LOADERS = []
try:
    import loaders.loader_exllama

    LOADERS.append(('ExLlama', loaders.loader_exllama.ExLlamaLoader))
except Exception as e:
    print("Can't import ExLlama loader")
    print(e)
try:
    import loaders.loader_exllamav2

    LOADERS.append(('ExLlamaV2', loaders.loader_exllamav2.ExLlamaV2Loader))
except Exception as e:
    print("Can't import ExLlamaV2 loader")
    print(e)
try:
    import loaders.loader_awq

    LOADERS.append(('AutoAWQ', loaders.loader_awq.AWQLoader))
except Exception as e:
    print("Can't import AutoAWQ loader")
    print(e)
try:
    import loaders.loader_transformers

    LOADERS.append(('Transformers', loaders.loader_transformers.TransformersLoader))
except Exception as e:
    print("Can't import Transformers loader")
    print(e)


# Por más contra intuitivo que sea, este widget es el que almacena el modelo.
# Aca se elige y se carga el modelo.
class LoaderModal(ModalScreen):
    class ModelChanged(Message):
        def __init__(self, model_name: str, model_loader: loaders.loader_generic.LoaderModel):
            self.model_name = model_name
            self.model_loader = model_loader
            super().__init__()
    def __init__(self):
        super().__init__()
        file_list = os.listdir('models')
        folder_list: List[str] = list(filter(lambda p: os.path.isdir('models/' + p), file_list))
        self.models_folders = folder_list
        self.model: loaders.loader_generic.LoaderModel = None
        self.model_name: str = ''

    def compose(self) -> ComposeResult:
        yield Grid(
            Select([(m, m) for m in self.models_folders], prompt="Select Model", id='select-loader-model'),
            Select(LOADERS, prompt='Select Loader', id='select-loader-loader'),
            Placeholder(),  # Reservar espacio para el coso de loading.
            Button("Close", variant="error", id='button-loader-close'),
            Button("Load", variant="primary", id='button-loader-load'),
        )
        # yield Footer()

    @on(Mount)
    def create_modal(self):
        self.query_one(Grid).border_title = "Select Model to Load"

    @on(Button.Pressed, selector='#button-loader-close')
    def handle_button_close(self, _event: Button.Pressed):
        self.app.pop_screen()

    @on(Button.Pressed, selector='#button-loader-load')
    def handle_button_load(self, _event: Button.Pressed):
        # Free memory no matter if something is loaded or if the modal has been configured correctly
        if self.model:
            self.model.unload_model()
            del self.model
            self.model: loaders.loader_generic.LoaderModel = None
        # Update footer status to unloaded state.
        self.app.bind(keys='f1', action='model_selection', description="Models")
        select_model: Select = self.query_one(selector='#select-loader-model', expect_type=Select)
        model_folder: str = select_model.value
        select_loader: Select = self.query_one(selector='#select-loader-loader', expect_type=Select)
        loader_class: loaders.loader_generic.LoaderModel = select_loader.value
        if loader_class and model_folder:
            self.query_one('#button-loader-close').disabled = True
            self.query_one('#button-loader-load').disabled = True
            select_model.disabled = True
            select_loader.disabled = True
            # animation
            loading = LoadingIndicator()
            self.query_one(Placeholder).styles.display = 'none'
            self.mount(loading, before='#button-loader-close')
            # cargar el modelo LLM
            self.load_model()
        else:
            # Cerrar el modal cuando tenía un modelo cargado, implica que lo eliminamos de memoria
            self.app.pop_screen()

    # El modelo terminó de cargar
    @on(Worker.StateChanged)
    def handle_worker_finished(self, event: Worker.StateChanged):
        if event.worker.is_finished:
            # Habilitar de nuevo el modal
            self.query_one('#button-loader-close').disabled = False
            self.query_one('#button-loader-load').disabled = False
            self.query_one('#select-loader-model').disabled = False
            self.query_one('#select-loader-loader').disabled = False
            # Quitar la animación de cargando y devolver el espacio para que no se achique el modal
            self.query_one(LoadingIndicator).remove()
            self.query_one(Placeholder).styles.display = 'block'
            if self.model_name:  # Poner el nombre del modelo cargado como estado
                self.post_message(LoaderModal.ModelChanged(model_name=self.model_name, model_loader=self.model))

            self.dismiss()  # Cerrar el modal automáticamente

    @work(exclusive=True, thread=True)
    async def load_model(self):
        # Uso un thread para no congelar la interfaz
        select_loader: Select = self.query_one(selector='#select-loader-loader', expect_type=Select)
        loader_class: Type[loaders.loader_generic.LoaderModel] = select_loader.value
        select_model: Select = self.query_one(selector='#select-loader-model', expect_type=Select)
        model_folder: str = select_model.value
        # Aca pasa lo pesado
        self.model: loaders.loader_generic.LoaderModel = loader_class('models/' + model_folder, '')
        self.model_name = model_folder
