from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

from loaders.loader_generic import LoaderModel


class AWQLoader(LoaderModel):
    def __init__(self, model_dir_path: str, model_file_path: str):
        super().__init__(model_dir_path, model_file_path)
        # st_pattern = os.path.join(model_dir_path, "*.safetensors")
        # model_path = glob.glob(st_pattern)  # Buscar cualquier archivo safetensors
        self.model = AutoAWQForCausalLM.from_quantized(model_dir_path, fuse_layers=True)
        # self.model = AutoAWQForCausalLM.from_pretrained(model_dir_path, model_path[0], fuse_layers=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir_path)

    # Mover el max a otro lado
    def loader_inference(self, text_prompt: str, max_new_tokens: int = 150, seed: int = -1):
        tokens_input = self.tokenizer(text_prompt, return_tensors='pt').to("cuda")
        tokens_output = self.model.generate(
            tokens_input.input_ids, max_new_tokens=max_new_tokens, pad_token_id=self.tokenizer.eos_token_id)
        decoded_output = self.tokenizer.batch_decode(tokens_output, skip_special_tokens=True)
        return decoded_output[0]

    def unload_model(self):
        del self.tokenizer
        self.tokenizer = None
        del self.model
        self.model = None
