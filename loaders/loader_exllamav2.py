from exllamav2 import ExLlamaV2, ExLlamaV2Config, ExLlamaV2Cache, ExLlamaV2Tokenizer
from exllamav2.generator import ExLlamaV2BaseGenerator, ExLlamaV2Sampler

from loaders.loader_generic import LoaderModel


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

    # dos infer, una recibe el settngs y la otra lo arma
    def loader_inference(self, text_prompt: str,
                         inference_settings: ExLlamaV2Sampler.Settings = ExLlamaV2Sampler.Settings(),
                         max_new_tokens: int = 150, seed: int = -1):
        output = self.generator.generate_simple(text_prompt, inference_settings, max_new_tokens, seed)
        return output

    def unload_model(self):
        del self.generator
        del self.cache
        del self.tokenizer
        del self.model
        del self.configuration



if __name__ == '__main__':
    model_dir = "/run/media/peka/DATOS/coso_llm/models/airoboros-l2-7B-gpt4-m2.0-GPTQ"
    loader = LoaderModel(model_dir)
    print("Output:")
    print(loader.loader_inference("A continuación van dos chistes sobre perros:\n1) "))
