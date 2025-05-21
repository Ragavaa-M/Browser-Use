import json

def render_report(history_data: dict, exclude_accordion=False) -> str:
    report_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Run Report</title>
        <link rel="stylesheet" type="text/css" href="/static/report.css">
        <script>
        document.addEventListener("DOMContentLoaded", function () {
            const headers = document.querySelectorAll(".accordion-header");
            headers.forEach(header => {
                header.addEventListener("click", function () {
                    const content = this.nextElementSibling;
                    content.style.display = content.style.display === "block" ? "none" : "block";
                });
            });

            const modal = document.getElementById("screenshotModal");
            const modalImg = document.getElementById("modalImage");
            const closeModal = document.getElementsByClassName("close")[0];

            document.querySelectorAll(".screenshot").forEach(img => {
                img.addEventListener("click", function () {
                    modal.style.display = "block";
                    modalImg.src = this.src;
                });
            });

            closeModal.onclick = function () {
                modal.style.display = "none";
            };

            window.onclick = function (event) {
                if (event.target === modal) {
                    modal.style.display = "none";
                }
            };
        });
        </script>
    </head>
    <body>
    """
    if not exclude_accordion:
        report_content += download_button_html(list(history_data.keys()))
    report_content += """
        <h1>Test Run Report</h1>
        <!-- Modal for screenshots -->
        <div id="screenshotModal" class="modal">
            <span class="close">&times;</span>
            <img id="modalImage" class="modal-content">
        </div>"""
    overall_duration = 0
    overall_status = "Success"

    # Calculate overall duration and status
    for task_name, task_data in history_data.items():
        steps = task_data.get("history", [])
        tot_duration = 0
        task_status = "Failure"
        if steps and steps[-1].get("result", [{}])[0].get("success", False):
            task_status = "Success"

        # Update overall status if any task fails
        if task_status == "Failure":
            overall_status = "Failure"

        # Calculate total duration for the task
        for step in steps:
            metadata = step.get("metadata", {})
            start = metadata.get("step_start_time", 0)
            end = metadata.get("step_end_time", 0)
            tot_duration += round(end - start, 2)
        overall_duration += tot_duration

    # Add summary section at the top
    report_content += f"""
    <div class="summary">
        <h2>Overall Test Run Summary</h2>
        <p><strong>Status:</strong> {overall_status}</p>
        <p><strong>Total Duration:</strong> {round(overall_duration, 2)} seconds</p>
    </div>
    """

    if exclude_accordion:
        # Render report without accordion HTML
        for task_name, task_data in history_data.items():
            steps = task_data.get("history", [])
            tot_duration = 0
            task_status = "Failure"
            if steps and steps[-1].get("result", [{}])[0].get("success", False):
                task_status = "Success"

            # Calculate total duration for the task
            for step in steps:
                metadata = step.get("metadata", {})
                start = metadata.get("step_start_time", 0)
                end = metadata.get("step_end_time", 0)
                tot_duration += round(end - start, 2)

            # Add plain section for the task
            report_content += f"""
            <div class="task-section">
                <h2>Task: {task_name}</h2>
                <div>
                    <span>Status: {task_status}</span> | <span>Total Duration: {round(tot_duration, 2)} seconds</span>
                </div>
            """

            # Add table for the task
            report_content += """
            <table>
                <tr>
                    <th>Step</th>
                    <th>Description</th>
                    <th>Screenshot</th>
                    <th>Expected Result</th>
                    <th>Actual Result</th>
                    <th>Input Tokens</th>
                    <th>Action</th>
                </tr>
            """

            for i, step in enumerate(steps):
                model_output = step.get("model_output", {})
                current_state = model_output.get("current_state", {}) if model_output else {}
                actions = model_output.get("action", []) if model_output else []
                metadata = step.get("metadata", {})
                base64_image = step.get("state", {}).get("screenshot", "")

                action_html = "<ul class='action-log-list'>"
                for action in actions:
                    action_type = list(action.keys())[0]
                    action_data = action[action_type]
                    action_html += f"<li><strong>{action_type}:</strong><ul>"
                    for key, value in action_data.items():
                        action_html += f"<li><strong>{key}:</strong> {value}</li>"
                    action_html += "</ul></li>"
                action_html += "</ul>"

                if i + 1 < len(steps):
                    next_step = steps[i + 1]
                    if isinstance(next_step, dict) and next_step.get("model_output"):
                        next_eval = (
                            next_step["model_output"]
                            .get("current_state", {})
                            .get("evaluation_previous_goal", "N/A")
                        )
                    else:
                        next_eval = "N/A"
                else:
                    if task_status == "Success":
                        next_eval = "Successfully executed all the steps."
                    else:
                        next_eval = "Failed to execute."

                report_content += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{current_state.get("memory", "")}</td>
                    <td>"""
                if base64_image:
                    report_content += f"""<img src="data:image/png;base64,{base64_image}" class="screenshot" alt="Step {i} screenshot">"""
                report_content += """</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td class="action-log"><div class="action-log-wrapper">{}</div></td>
                </tr>
                """.format(
                    current_state.get("next_goal", ""),
                    next_eval,
                    metadata.get("input_tokens", ""),
                    action_html
                )

            report_content += '</table></div>'
    else:
        # Generate accordions for each task
        for task_name, task_data in history_data.items():
            steps = task_data.get("history", [])
            tot_duration = 0
            task_status = "Failure"
            if steps and steps[-1].get("result", [{}])[0].get("success", False):
                task_status = "Success"

            # Calculate total duration for the task
            for step in steps:
                metadata = step.get("metadata", {})
                start = metadata.get("step_start_time", 0)
                end = metadata.get("step_end_time", 0)
                tot_duration += round(end - start, 2)

            # Add accordion for the task
            accordion_class = "accordion open" if exclude_accordion else "accordion"
            report_content += f"""
            <div class="{accordion_class}">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div>
                        <strong>Task:</strong> {task_name}
                    </div>
                    <div>
                        <span>Status: {task_status}</span> | <span>Total Duration: {round(tot_duration, 2)} seconds</span>
                    </div>
                </div>
                <div class="accordion-content" style="display:block;">
            """

            # Add table for the task
            report_content += """
            <table>
                <tr>
                    <th>Step</th>
                    <th>Description</th>
                    <th>Screenshot</th>
                    <th>Expected Result</th>
                    <th>Actual Result</th>
                    <th>Input Tokens</th>
                    <th>Action</th>
                </tr>
            """

            for i, step in enumerate(steps):
                model_output = step.get("model_output", {})
                current_state = model_output.get("current_state", {}) if model_output else {}
                actions = model_output.get("action", []) if model_output else []
                metadata = step.get("metadata", {})
                base64_image = step.get("state", {}).get("screenshot", "")

                action_html = "<ul class='action-log-list'>"
                for action in actions:
                    action_type = list(action.keys())[0]
                    action_data = action[action_type]
                    action_html += f"<li><strong>{action_type}:</strong><ul>"
                    for key, value in action_data.items():
                        action_html += f"<li><strong>{key}:</strong> {value}</li>"
                    action_html += "</ul></li>"
                action_html += "</ul>"

                if i + 1 < len(steps):
                    next_step = steps[i + 1]
                    if isinstance(next_step, dict) and next_step.get("model_output"):
                        next_eval = (
                            next_step["model_output"]
                            .get("current_state", {})
                            .get("evaluation_previous_goal", "N/A")
                        )
                    else:
                        next_eval = "N/A"
                else:
                    if task_status == "Success":
                        next_eval = "Successfully executed all the steps."
                    else:
                        next_eval = "Failed to execute."

                report_content += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{current_state.get("memory", "")}</td>
                    <td>"""
                if base64_image:
                    report_content += f"""<img src="data:image/png;base64,{base64_image}" class="screenshot" alt="Step {i} screenshot">"""
                report_content += """</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td class="action-log"><div class="action-log-wrapper">{}</div></td>
                </tr>
                """.format(
                    current_state.get("next_goal", ""),
                    next_eval,
                    metadata.get("input_tokens", ""),
                    action_html
                )

            report_content += '</table></div></div>'

    report_content += "</body></html>"
    return report_content

def download_button_html(tasks):
    return """
    <form action="/download_pdf" method="post" style="position:absolute;top:20px;right:30px;">
        {}
        <button type="submit" class="download-btn">Download Report as PDF</button>
    </form>
    """.format(''.join(f'<input type="hidden" name="tasks[]" value="{task}"/>' for task in tasks))