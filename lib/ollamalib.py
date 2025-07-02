import ollama
import config as cfg

model = cfg.Ollama_Model

# Calculate minimum requirement #TODO
"""
def CalculateMinReqs(model):
    # Compare weight to GPU VRAM and if more want user of performance issues
    
    # if too big inform user if they want to change models

    return
"""

# Function to ask Ollama a question
def askOllama(question):
    response: ollama.ChatResponse = ollama.chat(model=cfg.model, messages=[{"role": "user", "content": question}])
    raw_answer = response.message.content
    # print(f"Ollama: {raw_answer}") # Debug, print direct response from ollama model
    return raw_answer

# Function to format answer, removing thinking text from thinking model
def formatAnswer(answer):
    # if think tags exist:
    if "<think>" in answer and "</think>" in answer:
        # split answer using the </think> string
        before, after = answer.split("</think>", 1)
        # return the right side of our stripped string
        return after.strip()
    # return non-stripped string if it doesn't contain think tags (for non-thinking models)
    return answer


