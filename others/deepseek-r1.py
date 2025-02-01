import ollama

client = ollama.Client()

model = "deepseek-r1:1.5b"
prompt = "Are you better than OpenAI model?"

response = client.generate(
    model=model,
    prompt=prompt)

print("Response from ollama")
print(response.response)
