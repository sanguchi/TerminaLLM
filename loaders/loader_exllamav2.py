from exllamav2 import ExLlamaV2, ExLlamaV2Config, ExLlamaV2Cache, ExLlamaV2Tokenizer
from exllamav2.generator import ExLlamaV2BaseGenerator, ExLlamaV2Sampler
from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal, Grid
from textual.reactive import var, reactive
from textual.validation import Integer, Number
from textual.widget import Widget
from textual.widgets import Label, Input, Footer

from loaders.loader_generic import LoaderModel, LoaderSettings


# Bueno, para hacerla corta, hay que hacer una clase Loader o algo asi.
# Usamos el modelo directamente con unas funciones o usamos el Loader?
# Deberia haber una clase abstracta Model y usar herencia
# El loader debería heredar de Loader y devolver una subclase de Model?


class ExLlamaV2Loader(LoaderModel):
    def __init__(self, model_dir_path: str, model_file_path: str = ''):
        super().__init__(model_dir_path, model_file_path)

        self.configuration = ExLlamaV2Config()
        self.configuration.model_dir = model_dir_path
        self.configuration.prepare()
        self.model = ExLlamaV2(self.configuration)
        self.model.load()
        self.tokenizer = ExLlamaV2Tokenizer(self.configuration)
        self.cache = ExLlamaV2Cache(self.model)
        self.generator = ExLlamaV2BaseGenerator(self.model, self.cache, self.tokenizer)
        self.settings = ExLlamaV2Settings()
        self.settings.model_name = model_dir_path.split('/')[1]

    # dos infer, una recibe el settngs y la otra lo arma
    def loader_inference(self, text_prompt: str, seed: int = -1):
        max_new_tokens = self.settings.max_new_tokens
        inference_settings = self.settings.sampler_settings
        print(max_new_tokens, inference_settings.temperature)
        output = self.generator.generate_simple(text_prompt, inference_settings, max_new_tokens, seed)
        return output

    def unload_model(self):
        del self.generator
        del self.cache
        del self.tokenizer
        del self.model
        del self.configuration

        # Realmente no sé si sea buena idea meter la logica de la UI en la logica del modelo, pero bueno.


# Este settings se instancia en la creacion de cada Loader
# El Loader siempre tiene una instancia de esto y la usa para la inferencia.
class ExLlamaV2Settings(LoaderSettings):
    max_new_tokens = 150
    sampler_settings = ExLlamaV2Sampler.Settings()
    model_name = reactive('')

    def compose(self) -> ComposeResult:
        # Header part
        with Grid():
            yield Label("Settings for ExLLaMaV2 Loader", id='label_title')
            yield Label("Model Loaded", id='label_model')
            yield Input(value=self.model_name, disabled=True)
            # Settings pairs label <-> input
        # Settings widgets
        with VerticalScroll():
            with Grid():
                yield Label("max_new_tokens")
                yield Input(value=str(self.max_new_tokens), validators=[Integer(minimum=0)], id='input_max_new_tokens')
                yield Label("temperature")
                yield Input(value=str(self.sampler_settings.temperature), validators=[Number(minimum=0.01, maximum=1.99)], id='input_temperature')
        yield Footer()

    @on(Input.Changed, 'ExLlamaV2Settings Input')
    def update_values(self, event: Input.Changed):
        # print(event, event.validation_result, event.value)
        # Deberia encontrar una mejor alternativa a esto
        # Unir el settings <-> sample <-> ui | de alguna forma dinamica
        if event.validation_result and event.validation_result.is_valid:
            if event.input.id == 'input_max_new_tokens':
                self.max_new_tokens = int(event.value)
            elif event.input.id == 'input_temperature':
                self.sampler_settings.temperature = float(event.value)

    @on(Input.Submitted, 'ExLlamaV2Settings Input')
    def ignore_submits(self, event: Input.Submitted):
        event.prevent_default(True)
        if event.validation_result and not event.validation_result.is_valid:
            if event.input.id == 'input_max_new_tokens':
                event.input.value = str(self.max_new_tokens)
            elif event.input.id == 'input_temperature':
                event.input.value = str(self.sampler_settings.temperature)
