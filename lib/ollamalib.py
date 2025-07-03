import ollama
import config as cfg
import psutil
import GPUtil

model = cfg.Ollama_Model

import ollama
import config as cfg
import psutil
import GPUtil
import platform
import subprocess

model = cfg.Ollama_Model

def CalculateMinReqs(model="deepseek-r1"):
    """
    Checks if the system meets the minimum requirements for the specified Ollama model, in this case, deepsekr1.
    """
    model_requirements = {
        "deepseek-r1": {"vram": 26, "ram": 8}  # GB
    }

    if model not in model_requirements:
        print(f"Warning: No requirements specified for model '{model}'. Skipping check.")
        return True

    requirements = model_requirements[model]
    
    # Get system info
    gpus = GPUtil.getGPUs()
    gpu_vram_mb = gpus[0].memoryTotal if gpus else 0
    gpu_vram_gb = gpu_vram_mb / 1024  # VRAM in GB
    system_ram = psutil.virtual_memory().total / (1024**3)  # RAM in GB

    # Check requirements
    vram_ok = gpu_vram_gb >= requirements["vram"]
    ram_ok = system_ram >= requirements["ram"]

    if not vram_ok:
        print(f"Warning: Your system's VRAM ({gpu_vram_gb:.2f}GB / {gpu_vram_mb}MB) does not meet the recommended minimum of {requirements['vram']}GB for the '{model}' model.")
    if not ram_ok:
        print(f"Warning: Your system's RAM ({system_ram:.2f}GB) does not meet the recommended minimum of {requirements['ram']}GB for the '{model}' model.")

    return vram_ok and ram_ok

# Calculate minimum requirement #TODO


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


