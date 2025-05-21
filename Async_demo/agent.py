from flask import Flask, render_template, request, Response, send_file
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv
import asyncio
import os
import tempfile
import subprocess
from weasyprint import HTML, CSS
import io

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

llm_azure = AzureChatOpenAI(
    model="gpt-4o",
    api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('AZURE_OPENAI_API_ENDPOINT'),
    api_key=SecretStr(os.getenv('AZURE_OPENAI_API_KEY')),
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
    global history_data
    tasks = request.form.getlist('tasks[]')
    raw_results = asyncio.run(run_tasks_concurrently(tasks))
    history_data = {task: raw_result for task, raw_result in zip(tasks, raw_results)}
    html_report = render_report(history_data)
    return Response(html_report, mimetype='text/html')

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    global history_data
    html_report = render_report(history_data, exclude_accordion=True)
    pdf_io = io.BytesIO()
    HTML(string=html_report).write_pdf(
        pdf_io,
        stylesheets=[CSS(r'C:\Users\mragavaa\Desktop\Autogen\ollama-venv\Code_Files\Async_demo\static\report.css')],
        presentational_hints=True,
        optimize_size=('images',),
        zoom=1,
    )
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='report.pdf')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)