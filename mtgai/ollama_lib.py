import ollama
import config as cfg

# Calculate minimum requirement #TODO
"""
def CalculateMinReqs(model):
    # Compare weight to GPU VRAM and if more want user of performance issues
    
    # if too big inform user if they want to change models

    return
"""

# function to check if Ollama is running TODO

def CheckOllamaRunning():

    # is your fridge running?

    return None # better go catch it

# function to start Ollama service TODO
def StartOllama():

    # I know what's wrong with it, it got no gas in it!

    return None

# function to kill Ollama service TODO
def TerminateOllama():

    # the boy who lived, come to die

    return None

# Function to ask Ollama a question
def askOllama(question):
    response: ollama.ChatResponse = ollama.chat(model=cfg.Ollama_Model, messages=[{"role": "user", "content": question}])
    raw_answer = response.message.content
    # print(f"Ollama: {raw_answer}") # Debug, print direct response from ollama model
    return raw_answer

# Function to format answer, removing thinking text from thinking model
def formatAnswer(answer):
    # think tags exist, remove thinking portions
    if "<think>" in answer and "</think>" in answer:
        # split answer using the </think> string
        before, after = answer.split("</think>", 1)
        # return the right side of our stripped string
        return after.strip()
    # return non-stripped string if it doesn't contain think tags (for non-thinking models)
    return answer


#print(formatAnswer(askOllama("Why is the sky blue?")))
print(ollama.show(cfg.Ollama_Model))