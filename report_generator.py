import json

def render_report(json_file_path: str) -> str:
    # Load JSON data from the file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        history_data = json.load(file)

    # Extract the required data from the JSON
    steps = history_data.get("history", [])
    tot_duration = 0
    action_log = ""

    # Table structure for the report
    report_content = """
    <html>
    <head>
        <title>Task Report</title>
        <style>
        html {
            font-size: 16px;
        }

        body {
            font-family: Arial, sans-serif;
            margin: 2rem;
            padding: 0;
            box-sizing: border-box;
            max-width: 100%;
            overflow-x: hidden;
        }

        h1, h3 {
            color: #333;
            margin-bottom: 1rem;
        }

        table {
            width: 100%;
            max-width: 100%;
            border-collapse: collapse;
            margin-top: 2rem;
            overflow-x: auto;
            display: block;
        }

        th, td {
            padding: 1em;
            text-align: left;
            border: 1px solid #ccc;
            vertical-align: top;
        }

        th {
            background-color: #f4f4f4;
        }

        .action-log {
            background-color: #f9f9f9;
            padding: 1em;
            border-radius: 0.5em;
            font-size: 0.9rem;
        }

        img {
            max-width: 15rem;
            height: auto;
            display: block;
            margin: 0.5rem 0;
        }

        ul {
            padding-left: 1.5rem;
            margin: 0;
        }

        li {
            margin-bottom: 0.5em;
        }

        @media (max-width: 768px) {
            body {
                margin: 1rem;
            }

            table, th, td {
                font-size: 0.9rem;
            }

            img {
                max-width: 100%;
            }
        }
    </style>

    </head>
    <body>
        <h1>Task Execution Report</h1>
        <h3>Total Duration: <span id="total-duration">0</span> seconds</h3>
        <h3>Status: <span id="status"></span></h3>
        <table>
            <tr>
                <th>Step</th>
                <th>Description</th>
                <th>Screenshot</th>
                <th>Expected Result</th>
                <th>Actual Result</th>
                <th>Step Duration (s)</th>
                <th>Action Log</th>
            </tr>
    """
    
    for step_index, step in enumerate(steps):
        model_output = step.get("model_output", {})
        start_duration = step.get("metadata", {}).get("step_start_time", 0)
        end_duration = step.get("metadata", {}).get("step_end_time", 0)
        duration = round(end_duration - start_duration, 2)
        tot_duration += duration
        
        current_state = model_output.get("current_state", {})
        eval = current_state.get("evaluation_previous_goal", "N/A")
        next_goal = current_state.get("next_goal", "N/A")
        base64_image = step.get("state", {}).get("screenshot", "N/A")
        actual_result = step.get("result", [{}])[0].get("extracted_content", "N/A")
        
        # Prepare Action Log
        actions = model_output.get("action", [])
        action_html = "<ul>"
        for action in actions:
            action_type = list(action.keys())[0]  
            action_data = action[action_type]
            action_html += f"<li><strong>{action_type}:</strong><ul>"
            for key, value in action_data.items():
                action_html += f"<li><strong>{key}:</strong> {value}</li>"
            action_html += "</ul></li>"
        action_html += "</ul>"

        # Append step details to the table content
        report_content += f"""
        <tr>
            <td>{step_index + 1}</td>
            <td>{eval}</td>
            <td><img src="data:image/png;base64,{base64_image}" alt="screenshot"></td>
            <td>{next_goal}</td>
            <td>{actual_result}</td>
            <td>{duration}</td>
            <td class="action-log">{action_html}</td>
        </tr>
        """
    
    # Add the final step to the table
    if steps:
        last_step = steps[-1]
        result_list = last_step.get("result", [])
        success = result_list[0].get("success", "N/A")
        if success == True:
            success = "Success"
        else:
            success = "Failure"
        report_content += f"""
        <tr>
            <td colspan="6"><strong>Status</strong></td>
            <td>{success}</td>
        </tr>
        """

    # Close the table and finish the HTML content
    report_content += """
        </table>
    </body>
    </html>
    """
    
    # Replace total duration placeholder
    html_report = report_content.replace('<span id="total-duration">0</span>', f'<span id="total-duration">{tot_duration}</span>')
    html_report = html_report.replace('<span id="status"></span>', f'<span id="status">{success}</span>')
    return html_report

# Example usage
if __name__ == "__main__":
    json_file_path = "C:\\Users\\mragavaa\\Desktop\\Autogen\\ollama-venv\\Code_Files\\Browser-Use\\results\\task_Open_GitHub_and_Search_Repo_result.json"
    report = render_report(json_file_path)
    with open("report.html", "w", encoding="utf-8") as output_file:
        output_file.write(report)
    print("Report generated: report.html")
