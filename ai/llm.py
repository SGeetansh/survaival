from llama_cpp import Llama

class LocalLLM:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8,
            temperature=0.7,
            verbose=False
        )

    def generate(self, prompt: str) -> str:
        result = self.llm.create_completion(
            prompt=prompt,
            max_tokens=150,
            stop=["\n\n"]
        )
        return result["choices"][0]["text"].strip()