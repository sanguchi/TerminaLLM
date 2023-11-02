from dataclasses import dataclass
from typing import Any, Iterable, List

from awq import AutoAWQForCausalLM
from rich.highlighter import Highlighter
from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal, Grid
from textual.message import Message
from textual.reactive import reactive
from textual.suggester import Suggester
from textual.validation import Integer, Validator, ValidationResult
from textual.widget import Widget
from textual.widgets import Label, Input, Footer, Header
from textual.widgets._input import InputValidationOn
from transformers import AutoTokenizer

from loaders.loader_generic import LoaderModel, LoaderSettings


class AWQLoader(LoaderModel):
    def __init__(self, model_dir_path: str, model_file_path: str):
        super().__init__(model_dir_path, model_file_path)
        # st_pattern = os.path.join(model_dir_path, "*.safetensors")
        # model_path = glob.glob(st_pattern)  # Buscar cualquier archivo safetensors
        self.model = AutoAWQForCausalLM.from_quantized(model_dir_path, fuse_layers=True)
        # self.model = AutoAWQForCausalLM.from_pretrained(model_dir_path, model_path[0], fuse_layers=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir_path)
        self.settings = AWQSettings()
        self.settings.model_name = model_dir_path.split('/')[1]

    # Mover el max a otro lado
    def loader_inference(self, text_prompt: str, seed: int = -1):
        print("AWQ max_new_tokens:", self.settings.max_new_tokens)
        tokens_input = self.tokenizer(text_prompt, return_tensors='pt').to("cuda")
        tokens_output = self.model.generate(tokens_input.input_ids, max_new_tokens=self.settings.max_new_tokens,
                                            pad_token_id=self.tokenizer.eos_token_id)
        decoded_output = self.tokenizer.batch_decode(tokens_output, skip_special_tokens=True)
        return decoded_output[0]

    def unload_model(self):
        del self.tokenizer
        self.tokenizer = None
        del self.model
        self.model = None


class IntegerInput(Input):
    def __init__(self, value: int = 0, minimum: int = 0, maximum: int = 100, **kwargs):
        if 'validators' in kwargs:
            validators = set([Integer(minimum=minimum, maximum=maximum)] + kwargs.pop('validators'))
        else:
            validators = [Integer(minimum=minimum, maximum=maximum)]

        super().__init__(value=str(value), validators=validators, **kwargs)



# Este settings se instancia en la creacion de cada Loader
# El Loader siempre tiene una instancia de esto y la usa para la inferencia.
class AWQSettings(LoaderSettings):
    max_new_tokens: int = 150
    model_name = reactive('')

    def compose(self) -> ComposeResult:
        with Grid():
            yield Label("Settings for AutoAWQ Loader", id='label_title')
            yield Label("Model Loaded", id='label_model')
            yield Input(value=self.model_name, disabled=True)
            # Settings pairs label <-> input
        # Settings widgets
        with VerticalScroll():
            with Grid():
                yield Label("max_new_tokens")
                yield IntegerInput(value=150, minimum=0, maximum=4096, id='max_new_tokens')
        yield Footer()

    @on(Input.Changed)
    def handle_changed(self, event: Input.Changed):
        if event.validation_result and event.validation_result.is_valid:
            if type(event.control) == IntegerInput:
                setattr(self, event.input.id, int(event.value))
            if type(event.control) == Input:
                setattr(self, event.input.id, event.value)

    @on(Input.Submitted)
    def ignore_submits(self, event: Input.Submitted):
        event.prevent_default(True)
        if event.validation_result and not event.validation_result.is_valid:
            if hasattr(self, event.input.id):
                event.input.value = str(getattr(self, event.input.id))
