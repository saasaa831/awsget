import os
import datetime


def generate_html_report(test_suites, report_title="QA Test Report", output_file="qa_test_report.html"):
    """
    Generates a customizable QA HTML report with collapsible test suites and clickable test versions.
    :param test_suites: Dictionary of test suites containing lists of (version, test_results)
    :param report_title: Title of the HTML report
    :param output_file: Output HTML file name
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date: 2025-03-18

    def get_status_class(status):
        return {"pass": "pass", "fail": "fail", "skip": "skip"}.get(status.lower(), "")

    def generate_sidebar():
        """Generates the collapsible sidebar for test suites with circles aligned in a straight line."""
        total_cases = 0
        passed = 0
        failed = 0
        skipped = 0

        for suite_name, versions in test_suites.items():
            for version, test_results in versions:
                total_cases += len(test_results)
                passed += sum(1 for test in test_results if test["status"].lower() == "pass")
                failed += sum(1 for test in test_results if test["status"].lower() == "fail")
                skipped += sum(1 for test in test_results if test["status"].lower() == "skip")

        sidebar_content = f"""
        <div class="sidebar">
            <h3 style="text-align:center;">Test Suites</h3>
            <div style="text-align:left; padding-left: 20px;">
                <span style="background-color: green; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Pass: {passed} / {total_cases}<br>
                <span style="background-color: red; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Fail: {failed} / {total_cases}<br>
                <span style="background-color: orange; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Skipped: {skipped} / {total_cases}<br>
            </div>
            <ul class="suite-list">
        """
        for suite_name, versions in test_suites.items():
            suite_id = suite_name.replace(" ", "_").lower()
            sidebar_content += f"""
            <li>
                <span class="suite-header" onclick="toggleSuite('{suite_id}')">{suite_name}</span>
                <ul id="{suite_id}" class="suite-items hidden">
            """
            for i, (version, _) in enumerate(versions):
                sidebar_content += f"<li><a href='#' onclick='showReport(\"report_{suite_id}_{i}\")'>{suite_name} - v{version}</a></li>"
            sidebar_content += "</ul></li>"
        sidebar_content += "</ul></div>"
        return sidebar_content

    def generate_test_table(test_results):
        """Generates an HTML table for test results."""
        return """
        <table>
            <tr style="background-color: #4CAF50; color: white;">
                <th>Test Name</th>
                <th>Status</th>
                <th>Exec Time (s)</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Remarks</th>
            </tr>
            {}
        </table>
        """.format("".join(
            f"""
            <tr class='{get_status_class(test['status'])}'>
                <td>{test['test_name']}</td>
                <td>{test['status']}</td>
                <td>{test.get('execution_time', 'N/A')}</td>
                <td>{test['expected_results']}</td>
                <td>{test['actual_results']}</td>
                <td>{test['remarks']}</td>
            </tr>
            """ for test in sorted(test_results, key=lambda x: x['test_name'])
        ))

    def generate_test_suite_summary(test_results):
        """Generates the summary of pass/fail/skip for a test suite."""
        total = len(test_results)
        passed = sum(1 for test in test_results if test["status"].lower() == "pass")
        failed = sum(1 for test in test_results if test["status"].lower() == "fail")
        skipped = sum(1 for test in test_results if test["status"].lower() == "skip")

        return f"""
        <div style="text-align:left;">
            <span style="background-color: green; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Pass: {passed} / {total}
            <span style="background-color: red; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Fail: {failed} / {total}
            <span style="background-color: orange; display: inline-block; width: 15px; height: 15px; border-radius: 50%; margin-right: 5px;"></span> Skipped: {skipped} / {total}
        </div>
        """

    def generate_test_sections():
        """Generates test sections dynamically."""
        sections = []
        for suite_name, versions in test_suites.items():
            suite_id = suite_name.replace(" ", "_").lower()
            for i, (version, test_results) in enumerate(versions):
                sections.append(f"""
                <div id='report_{suite_id}_{i}' class='report-section hidden'>
                    <h3><u>{suite_name} - Version {version}</u></h3>
                    {generate_test_suite_summary(test_results)}
                    {generate_test_table(test_results)}
                </div>
                """)
        return "".join(sections)

    html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; margin: 0; }}
                .sidebar {{ width: 300px; background: #333; color: white; height: 100vh; padding-top: 20px; position: fixed; overflow-y: auto; }}
                .sidebar ul {{ list-style: none; padding: 0; }}
                .suite-header {{ cursor: pointer; padding: 10px; display: block; font-weight: bold; background: #444; }}
                .suite-header:hover {{ background: #575757; }}
                .suite-items {{ display: none; margin-left: 20px; }}
                .suite-items li a {{ display: block; padding: 5px; color: white; text-decoration: none; }}
                .suite-items li a:hover {{ background: #575757; }}
                .content {{ margin-left: 300px; padding: 20px; width: calc(100% - 270px); }}
                .hidden {{ display: none; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                .pass {{ background-color: #e6ffe6; }} /* Light green for pass */
                .fail {{ background-color: #ffe6e6; }} /* Light red for fail */
                .skip {{ background-color: #fff3e6; }} /* Light orange for skip */
            </style>
            <script>
                function toggleSuite(id) {{
                    var suite = document.getElementById(id);
                    suite.style.display = suite.style.display === 'block' ? 'none' : 'block';
                }}
                function showReport(id) {{
                    document.querySelectorAll('.report-section').forEach(el => el.classList.add('hidden'));
                    document.getElementById(id).classList.remove('hidden');
                }}
            </script>
        </head>
        <body>
            {generate_sidebar()}
            <div class="content">
                <h2 align="center">{report_title}</h2>
                <p align="center">Generated on: {timestamp}</p>
                {generate_test_sections()}
            </div>
        </body>
        </html>
        """

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_template)

    print(f"Report generated successfully: {output_file}")


# Example Usage with Sample Data
test_suites = {
    "Regression Suite": [
        ("1.0", [
            {"test_name": "Login Test", "status": "Pass", "execution_time": "2.1", "expected_results": "Success",
             "actual_results": "Success", "remarks": "OK"},
            {"test_name": "Logout Test", "status": "Pass", "execution_time": "1.5", "expected_results": "Success",
             "actual_results": "Success", "remarks": "OK"}
        ]),
        ("2.0", [
            {"test_name": "Signup Test", "status": "Fail", "execution_time": "3.5",
             "expected_results": "Validation error", "actual_results": "Unexpected error", "remarks": "Bug"},
            {"test_name": "Password Reset Test", "status": "Skip", "execution_time": "N/A",
             "expected_results": "Reset email sent", "actual_results": "N/A", "remarks": "Not implemented"}
        ])
    ],
    "Smoke Tests": [
        ("1.1", [
            {"test_name": "Cart Test", "status": "Pass", "execution_time": "1.8", "expected_results": "Item added",
             "actual_results": "Item added", "remarks": "Success"}
        ])
    ]
}

# Generate the report
generate_html_report(test_suites, report_title="QA Test Report", output_file="qa_test_report.html")
