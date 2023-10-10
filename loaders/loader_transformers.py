import os.path

from transformers import AutoModelForCausalLM, AutoTokenizer

from loaders.loader_generic import LoaderModel


# Bueno, para hacerla corta, hay que hacer una clase Loader o algo asi.
# Usamos el modelo directamente con unas funciones o usamos el Loader?
# Deberia haber una clase abstracta Model y usar herencia
# El loader debería heredar de Loader y devolver una subclase de Model?


# Path must be a fullpath
class TransformersLoader(LoaderModel):
    def __init__(self, model_dir_path: str, model_file_path: str = ''):
        super().__init__(model_dir_path, model_file_path)
        model_dir_path = os.path.abspath(model_dir_path)
        model_file_path = os.path.abspath(model_file_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir_path, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir_path)

    # dos infer, una recibe el settngs y la otra lo arma
    def loader_inference(self, text_prompt: str, max_new_tokens: int = 150, seed: int = -1):
        tokens_input = self.tokenizer(text_prompt, return_tensors='pt').to("cuda")
        print(tokens_input)
        tokens_output = self.model.generate(tokens_input.input_ids, max_new_tokens=max_new_tokens)
        decoded_output = self.tokenizer.batch_decode(tokens_output, skip_special_tokens=True)
        return decoded_output[0]

    def unload_model(self):
        del self.model
        self.model = None
