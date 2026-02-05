from llama_cpp import Llama
import os

MODEL_PATH = "models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

print("Checking model path...")
assert os.path.exists(MODEL_PATH), "Model file not found!"

print("Loading model...")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=8, verbose=False)

print("Running inference...")
result = llm.create_completion(
    prompt="You are an AI judge. Say one sentence about survival.",
    max_tokens=50,
)

print("\n--- MODEL OUTPUT ---")
print(result["choices"][0]["text"].strip())
print("--------------------")

print("\n✅ All prerequisites are installed and working.")
