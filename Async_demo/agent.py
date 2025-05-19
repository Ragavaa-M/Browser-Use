from flask import Flask, render_template, request, Response
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import asyncio
import os

from browser_use import Agent
from report_generator import render_report  

load_dotenv()

app = Flask(__name__)

llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=SecretStr(os.getenv('GEMINI_API_KEY')),
    temperature=0.2,
    seed=42
)

async def run_agent(task: str):
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    return history.model_dump()

async def run_tasks_concurrently(tasks):
    coros = [run_agent(task) for task in tasks if task.strip()]
    return await asyncio.gather(*coros)  

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run():
    tasks = request.form.getlist('tasks[]')
    raw_results = asyncio.run(run_tasks_concurrently(tasks))
    history_data = {task: raw_result for task, raw_result in zip(tasks, raw_results)}
    html_report = render_report(history_data)
    return Response(html_report, mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)