import glob
import os

from exllama.generator import ExLlamaGenerator
from exllama.model import ExLlamaConfig, ExLlama, ExLlamaCache
from exllama.tokenizer import ExLlamaTokenizer

from loaders.loader_generic import LoaderModel


# Bueno, para hacerla corta, hay que hacer una clase Loader o algo asi.
# Usamos el modelo directamente con unas funciones o usamos el Loader?
# Deberia haber una clase abstracta Model y usar herencia
# El loader debería heredar de Loader y devolver una subclase de Model?



class ExLlamaLoader(LoaderModel):
    def __init__(self, model_dir_path: str, model_file_path: str = ''):
        super().__init__(model_dir_path, model_file_path)
        tokenizer_path = os.path.join(model_dir_path, "tokenizer.model")
        model_config_path = os.path.join(model_dir_path, "config.json")
        st_pattern = os.path.join(model_dir_path, "*.safetensors")
        model_path = glob.glob(st_pattern)
        # raise Exception("XDD")
        self.configuration = ExLlamaConfig(model_config_path)
        self.configuration.model_path = model_path
        self.model = ExLlama(self.configuration)
        self.tokenizer = ExLlamaTokenizer(tokenizer_path)
        self.cache = ExLlamaCache(self.model)
        self.generator = ExLlamaGenerator(self.model, self.tokenizer, self.cache)

    # dos infer, una recibe el settngs y la otra lo arma
    def loader_inference(self, text_prompt: str, max_new_tokens: int = 150, seed: int = -1):
        output = self.generator.generate_simple(text_prompt, max_new_tokens=max_new_tokens)
        return output

    def unload_model(self):
        del self.generator
        del self.cache
        del self.tokenizer
        del self.model
        del self.configuration
