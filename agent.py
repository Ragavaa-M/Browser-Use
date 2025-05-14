from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
import os
import asyncio
import json
import sys
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from browser_use.agent.service import log_response
from report_generator import render_report
import pathlib
load_dotenv()

try:
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            remote_debugging_port=7555
        )
    )

except Exception as e:
    print(f"Error initializing browser: {e}")
    print("Ensure Chrome is running in debug mode on port 9222.")
    sys.exit(1)

extend_system_prompt = ""
override_system_prompt = """You are a web automation expert. When automating web pages:

1. Scrolling Interactions:
   - Identify scrollable containers and content areas
   - Scroll to elements that are not in viewport
   - Handle infinite scrolling if present
   - Ensure elements are visible before interacting

2. Drag and Drop Operations:
   - Locate draggable elements and drop zones
   - Verify elements are draggable before attempting
   - Handle both HTML5 and JavaScript-based drag-drop
   - Confirm successful drop operation

3. Interactive Elements:
   - Check for clickable elements (buttons, links)
   - Handle hover menus and tooltips
   - Interact with sliders and range inputs
   - Manage modal dialogs and popups
   - Work with dynamic content loading

4. Form Interactions:
   - Fill form fields in correct order
   - Handle autocomplete suggestions
   - Manage dropdown selections
   - Upload files when needed

5. Navigation:
   - Handle multi-step processes
   - Verify page state before proceeding
   - Wait for loading states to complete
   - Check for success/error messages

6.Selecting Options:
    - Retrieve the list of available options
    - Verify that options are interactable and not disabled
    - Always select the top (first) available option unless specified otherwise
    - Confirm the selection was successful by checking the dropdown's displayed value   

Always ensure elements are interactive before attempting operations and handle any loading states or animations."""

def load_tasks():
    with open('tasks 3.json', 'r') as f:
        return json.load(f)

def filter_tasks_by_tag(tasks, tag):
    return [task for task in tasks if tag.lower() in [t.lower() for t in task['tags']]]

llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=SecretStr(os.getenv('GEMINI_API_KEY')),
    temperature=0.2,
    seed=42
)
planner_llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    api_key=SecretStr(os.getenv('GEMINI_API_KEY')),
    temperature=0.2,
    max_tokens=1000
)
async def run_task(task):
    try:
        agent = Agent(
            task=task['task'],
            llm=llm,
        )
        history = await agent.run()
        await browser.close()
        dump = history.model_dump()

        os.makedirs('results', exist_ok=True)

        filename = f"results/task_{task['title'].replace(' ', '_')}_result.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dump, f, indent=2)
           
        print(f"Results saved to: {filename}")
        return history
    except Exception as e:
        print(f"Error executing task {task['id']}: {str(e)}")
        return None
    
async def main():
    # Check if tag is provided
    if len(sys.argv) != 2:
        print("Usage: python agent.py <tag>")
        sys.exit(1)

    tag = sys.argv[1]
    tasks = load_tasks()
    filtered_tasks = filter_tasks_by_tag(tasks, tag)
    print(filtered_tasks.title())
    if not filtered_tasks:
        print(f"No tasks found with tag: {tag}")
        sys.exit(0)

    print(f"Found {len(filtered_tasks)} tasks with tag '{tag}'")

    history_dict = {} 
    for task in filtered_tasks:
        history = await run_task(task)
        title = task['title']
        print(title)
        history_dict[title] = history

if __name__ == "__main__":
    asyncio.run(main())