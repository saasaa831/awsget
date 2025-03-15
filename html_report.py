import os
import datetime

def generate_html_report(test_result_sets, report_title="QA Test Report", output_file="qa_test_report.html"):
    """
    Generates a customizable QA HTML report for multiple test result sets with a sidebar for navigation.
    :param test_result_sets: List of tuples (set_name, version, test_results)
    :param report_title: Title of the HTML report
    :param output_file: Output HTML file name
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                display: flex;
                overflow-x: hidden;
            }}
            .sidebar {{
                width: 300px;
                background: #333;
                color: white;
                height: 100vh;
                padding-top: 20px;
                position: fixed;
                overflow-y: auto;
            }}
            .sidebar a {{
                display: block;
                padding: 10px;
                color: white;
                text-decoration: none;
                border-bottom: 1px solid gray;
            }}
            .sidebar a:hover {{
                background: #575757;
            }}
            .content {{
                margin-left: 0px;
                padding: 20px;
                width: calc(100% - 270px);
                overflow-x: auto;
            }}
            .container {{
                max-width: 1000px;
                margin: auto;
            }}
            h2, h3 {{
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                table-layout: fixed;
                word-wrap: break-word;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                word-break: break-word;
                overflow-wrap: break-word;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            .pass {{
                background-color: #c6efce;
            }}
            .fail {{
                background-color: #ffc7ce;
            }}
             .skip {{
                background-color: #FFA500;
            }}
            .set-header {{
                background-color: #f2f2f2;
                padding: 10px;
                font-size: 18px;
                text-align: center;
            }}
            .hidden {{
                display: none;
            }}

            /* Circle styles */
            .circle {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                color: white;
                font-size: 16px;
                text-align: center;
                display: inline-block;
                line-height: 40px;
                margin: 10px;
            }}
            .pass-circle {{
                background-color: #4CAF50;
            }}
            .fail-circle {{
                background-color: #FF6347;
            }}
            .skip-circle {{
                background-color: #FFA500;
            }}
            .total-circle {{
                background-color: #0000FF;
            }}
            /* Specific column width adjustments */
            .test-name-column {{
                width: 40%;
            }}
            .status-column {{
                width: 20%;
            }}
            .expected-results-column,
            .actual-results-column,
            .remarks-column {{
                width: 60%;
            }}
        </style>
        <script>
            function showReport(id) {{
                var sections = document.getElementsByClassName('report-section');
                for (var i = 0; i < sections.length; i++) {{
                    sections[i].classList.add('hidden');
                }}
                document.getElementById(id).classList.remove('hidden');
            }}
        </script>
    </head>
    <body>
        <div class="sidebar">
            <h3 style="text-align:center;">Test Suites</h3>
    """

    # Adding Overall Test Results Circle
    overall_pass = overall_fail = overall_skip = 0
    for _, _, test_results in test_result_sets:
        overall_pass += sum(1 for test in test_results if test['status'].lower() == 'pass')
        overall_fail += sum(1 for test in test_results if test['status'].lower() == 'fail')
        overall_skip += sum(1 for test in test_results if test['status'].lower() == 'skip')

    total_tests = overall_pass + overall_fail + overall_skip
    overall_pass_percentage = (overall_pass / total_tests) * 100 if total_tests > 0 else 0
    overall_fail_percentage = (overall_fail / total_tests) * 100 if total_tests > 0 else 0
    overall_skip_percentage = (overall_skip / total_tests) * 100 if total_tests > 0 else 0
    html_template += f"""
        <div style="text-align:center; margin-top: 20px;">
            <h3>Overall Test Results</h3>
            <div class="circle total-circle">{total_tests}</div>
            <div class="circle pass-circle">{overall_pass}</div>
            <div class="circle fail-circle">{overall_fail}</div>
            <div class="circle skip-circle">{overall_skip}</div>
        </div>
    """

    # Sidebar links for each test set
    for i, (set_name, version, _) in enumerate(test_result_sets):
        html_template += f"<a href='#' onclick='showReport(\"report_{i}\")'>{set_name} - v{version}</a>"

    html_template += """
        </div>
        <div class="content">
            <div class="container">
                <h2>{}</h2>
                <p>Generated on: {}</p>
    """.format(report_title, timestamp)

    # Add metrics for individual test suites
    for i, (set_name, version, test_results) in enumerate(test_result_sets):
        pass_count = sum(1 for test in test_results if test['status'].lower() == 'pass')
        fail_count = sum(1 for test in test_results if test['status'].lower() == 'fail')
        skip_count = sum(1 for test in test_results if test['status'].lower() == 'skip')
        total_count = pass_count + fail_count + skip_count
        # Display test suite pass/fail metrics as circles
        html_template += f"""
        <div id='report_{i}' class='report-section'>
        <div style="text-align:center;">
                <div class="circle total-circle">{total_count}</div>
                <div class="circle pass-circle">{pass_count}</div>
                <div class="circle fail-circle">{fail_count}</div>
                <div class="circle skip-circle">{skip_count}</div>
            </div>
            <h3 class='set-header'>{set_name} - Version {version}</h3>
            <table>
                <tr>
                    <th class="test-name-column">Test Name</th>
                    <th class="status-column">Status</th>
                    <th class="expected-results-column">Expected Results</th>
                    <th class="actual-results-column">Actual Results</th>
                    <th class="remarks-column">Remarks</th>
                </tr>
        """

        for test in test_results:
            status_class = "pass" if test['status'].lower() == "pass" else "fail" if test['status'].lower() == "fail" else "skip"
            html_template += f"""
           <tr class='{status_class}'>
                <td class="test-name-column">{test['test_name']}</td>
                <td class="status-column">{test['status']}</td>
                <td class="expected-results-column" style="white-space: normal;">{test['expected_results']}</td>
                <td class="actual-results-column" style="white-space: normal;">{test['actual_results']}</td>
                <td class="remarks-column">{test['remarks']}</td>
            </tr>
            """

        html_template += """
            </table>
        </div>
        """

    html_template += """
            </div>
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_template)

    print(f"Report generated successfully: {output_file}")


# Example usage:
test_result_sets = [
    ("Regression Suite", "1.0", [
        {"test_name": "Login Test", "status": "Pass", "execution_time": "2.1", "expected_results": "Successful login",
         "actual_results": "Successful login", "remarks": "Successful login"},
        {"test_name": "Signup Test", "status": "Fail", "execution_time": "3.5", "expected_results": "Validation error",
         "actual_results": "Validation error Validation error Validation error", "remarks": "Validation error"}
    ]),
    ("Smoke Tests", "1.2", [
        {"test_name": "Cart Test", "status": "Pass", "execution_time": "1.8", "expected_results": "Item added successfully",
         "actual_results": "Item added successfully", "remarks": "Item added successfully"},
        {"test_name": "Checkout Test", "status": "Pass", "execution_time": "2.5", "expected_results": "Order placed",
         "actual_results": "Order placed", "remarks": "Order placed"},
{"test_name": "Checkout Test", "status": "Skip", "execution_time": "2.5", "expected_results": "Order placed",
         "actual_results": "Order placed", "remarks": "Order placed"}
    ]),
    ("Performance Tests", "2.0", [
        {"test_name": "Load Test", "status": "Pass", "execution_time": "10.0", "expected_results": "System loads 5000 users",
         "actual_results": "System loads 5000 users", "remarks": "System is stable under load"},
        {"test_name": "Stress Test", "status": "Fail", "execution_time": "15.0", "expected_results": "System crashes",
         "actual_results": "System crashes", "remarks": "System crashed under stress"}
    ])
]

generate_html_report(test_result_sets)
