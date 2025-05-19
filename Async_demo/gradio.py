import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
import os
import asyncio
import json
from dotenv import load_dotenv
from browser_use import Agent

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=SecretStr(os.getenv('GEMINI_API_KEY')),
    temperature=0.2,
    seed=42
)

# Function to run a single task with Agent
async def run_agent(task: str):
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history.model_dump()

# Function to run multiple agents concurrently
async def run_tasks_concurrently(*tasks):
    coros = [run_agent(task) for task in tasks if task.strip()]
    results = await asyncio.gather(*coros)
    return tuple(json.dumps(result, indent=2) for result in results)

# Wrapper to run async function in Gradio
def run_tasks(*tasks):
    return asyncio.run(run_tasks_concurrently(*tasks))

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Multi-Agent Task Runner")

    task_inputs = []
    with gr.Row():
        for i in range(1, 11):
            task_input = gr.Textbox(label=f"Task {i}", placeholder=f"Enter task {i}")
            task_inputs.append(task_input)

    run_button = gr.Button("Generate")

    with gr.Row():
        result_outputs = []
        for i in range(1, 11):
            result_output = gr.Code(label=f"Agent {i} Output", language="json")
            result_outputs.append(result_output)

    run_button.click(run_tasks, inputs=task_inputs, outputs=result_outputs)

# Launch app
if __name__ == "__main__":
    demo.launch()
