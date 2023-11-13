import torch
from llama_index.llms import HuggingFaceLLM

class RAGLLM:
    """
    Retrieval-Augmented Generation Large-Language Model
    """
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def initialize_llm(self):
        llm = HuggingFaceLLM(
               context_window=4096,
                max_new_tokens=256,
                generate_kwargs={"temperature": 0.0, "do_sample": False},
                system_prompt=self.system_prompt,
                tokenizer_name="Salesforce/xgen-7b-8k-inst",
                model_name="Salesforce/xgen-7b-8k-inst",
                device_map="auto",
                tokenizer_kwargs={"trust_remote_code": True},
                model_kwargs={"torch_dtype": torch.bfloat16, "load_in_4bit": True},
            )
        return llm