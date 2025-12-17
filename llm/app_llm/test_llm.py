from llama_cpp import Llama

# Path to your quantized GGUF model
MODEL_PATH = "/app/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"

# Initialize model (loads into memory)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,          # context length
    n_threads=8,         # adjust based on CPU cores
    verbose=True,       # enable for detailed logs
    progress_bar=False    # show progress bar during generation
)

# Simple prompt
prompt = "Q: Explain what a large language model is in a concise way. A: "

# Generate response
output = llm(prompt, max_tokens=128, stop=["Q:", "\n"], echo=False)

# Print text result
print("Model output:\n")
print(output)

# llm = Llama(
#       model_path="./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
#       # n_gpu_layers=-1, # Uncomment to use GPU acceleration
#       # seed=1337, # Uncomment to set a specific seed
#       # n_ctx=2048, # Uncomment to increase the context window
# )
# output = llm(
#       "Q: Name the planets in the solar system? A: ", # Prompt
#       max_tokens=128, # Generate up to 32 tokens, set to None to generate up to the end of the context window
#       stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
#       echo=True # Echo the prompt back in the output
# ) # Generate a completion, can also call create_completion
# print(output['choices'][0]['text'])