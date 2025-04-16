import os
import datetime


def generate_html_report(test_suites, report_title="AMI Test Report(QA)", output_file="qa_test_report.html", runner_version="v1.0"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_status_class(status):
        return {"passed": "pass", "failed": "fail", "skipped": "skip"}.get(status.lower(), "")

    def generate_sidebar():
        total_cases = passed = failed = skipped = 0
        for versions in test_suites.values():
            for _, test_results in versions:
                total_cases += len(test_results)
                passed += sum(1 for t in test_results if t["status"].lower() == "passed")
                failed += sum(1 for t in test_results if t["status"].lower() == "failed")
                skipped += sum(1 for t in test_results if t["status"].lower() == "skipped")

        sidebar = f"""
        <div class="sidebar">
            <h3 style="text-align:center; color: white;">Test Suites</h3>
            <div class="summary-circles" style="text-align:left; padding-left: 20px; color: white">
                <span class="smcircle total" onclick="filterByStatus('all')"><center>Total: {total_cases}</center></span>
                <span class="smcircle pass" onclick="filterByStatus('pass')"><center>Pass: {passed}</center></span>
                <span class="smcircle fail" onclick="filterByStatus('fail')"><center>Fail: {failed}</center></span>
                <span class="smcircle skip" onclick="filterByStatus('skip')"><center>Skip: {skipped}</center></span>
            </div>
            <ul class="suite-list">
        """
        for suite_name, versions in test_suites.items():
            suite_id = suite_name.replace(" ", "_").lower()
            sidebar += f"""
            <li>
                <span class="suite-header" onclick="toggleSuite('{suite_id}')">{suite_name}</span>
                <ul id="{suite_id}" class="suite-items hidden">
            """
            for i, (version, _) in enumerate(versions):
                sidebar += f"<li><a href='#' onclick='showReport(\"report_{suite_id}_{i}\")'>{suite_name} - v{version}</a></li>"
            sidebar += "</ul></li>"
        sidebar += "</ul></div>"
        return sidebar

    def format_results(results):
        if results:
            if isinstance(results, list):
                text = ',<br>'.join(str(item) for item in results)
                return text
            elif isinstance(results, dict):
                text = ',<br>'.join(f"{key}: {value}" for key, value in results.items())
                return text
            else:
                return results
        else:
            return ''

    def generate_test_table(test_results):
        return """
        <table>
            <tr class="table-header">
                <th style="width: 20%">Test Name</th>
                <th style="width: 10%">Status</th>
                <th style="width: 25%">Expected</th>
                <th style="width: 30%">Actual</th>
                <th style="width: 20%">Remarks</th>
            </tr>
            {}
        </table>
        """.format("".join(
            f"""
            <tr class='{get_status_class(test['status'])}'>
                <td style="width: 20%">{test['test_name']}</td>
                <td style="width: 10%"><b>{test['status']}</b></td>
                <td style="width: 25%">{test['expected_results']}</td>
                <td style="width: 30%">{test['actual_results']}</td>
                <td style="width: 20%">{test['remarks']}</td>
            </tr>
            """ for test in test_results  # for test in sorted(test_results, key=lambda x: x['test_name'])
        ))

    def generate_test_suite_summary(test_results, suite_block_id):
        total = len(test_results)
        passed = sum(1 for t in test_results if t["status"].lower() == "passed")
        failed = sum(1 for t in test_results if t["status"].lower() == "failed")
        skipped = sum(1 for t in test_results if t["status"].lower() == "skipped")

        return f"""
        <div class="summary-circles" data-suite="{suite_block_id}">
            <span class="circle total" onclick="filterSuite('{suite_block_id}', 'all')">Total: {total}</span>
            <span class="circle pass" onclick="filterSuite('{suite_block_id}', 'pass')">Pass: {passed}</span>
            <span class="circle fail" onclick="filterSuite('{suite_block_id}', 'fail')">Fail: {failed}</span>
            <span class="circle skip" onclick="filterSuite('{suite_block_id}', 'skip')">Skip: {skipped}</span>
        </div>
        """

    def generate_test_sections():
        sections = []
        for suite_name, versions in test_suites.items():
            suite_id = suite_name.replace(" ", "_").lower()
            for i, (version, test_results) in enumerate(versions):
                block_id = f"report_{suite_id}_{i}"
                sections.append(f"""
                <div id="{block_id}" class="report-section hidden" data-statuses="{' '.join([get_status_class(t['status']) for t in test_results])}">
                    <h3><u>{suite_name} - Version {version}</u></h3>
                    {generate_test_suite_summary(test_results, block_id)}
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
            .sidebar {{ width: 300px; background: #333; height: 100vh; padding-top: 20px; position: fixed; overflow-y: auto; }}
            .sidebar ul {{ list-style: none; padding: 0; }}
            .suite-header {{ cursor: pointer; padding: 10px; display: block; font-weight: bold; background: #444; color: white; }}
            .suite-header:hover {{ background: #575757; }}
            .suite-items {{ display: none; margin-left: 20px; }}
            .suite-items li a {{ display: block; padding: 5px; color: white; text-decoration: none; }}
            .suite-items li a:hover {{ background: #575757; }}
            .content {{ margin-left: 300px; padding: 20px; width: calc(100% - 270px); }}
            .hidden {{ display: none; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; table-layout fixed; word-wrap: break-word;}}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; word-break: break-word; overflow-wrap: break-word;}}
            .pass {{ background-color: #e6ffe6; }}
            .fail {{ background-color: #ffe6e6; }}
            .skip {{ background-color: #fff3e6; }}
            .summary-circles {{ margin: 10px 0; }}
            .circle {{
                display: inline-block;
                padding: 6px 10px;
                margin: 5px 5px 5px 0;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
            }}
            .circle.pass {{ background-color: light green;}}
            .circle.fail {{ background-color: light red; }}
            .circle.skip {{ background-color: light orange;  }}
            .circle.total {{ background-color: lightblue;  }}
            .table-header {{ background-color: #4CAF50;  color: white; }}
            .smcircle {{
                display: inline-block;
                margin-right: 5px;
                border-radius: 50px;
                width: 100px;
                height: 15px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
            }}
            .smcircle.pass {{ background-color: green;}}
            .smcircle.fail {{ background-color: red; }}
            .smcircle.skip {{ background-color: orange;  }}
            .smcircle.total {{ background-color: blue;  }}
        </style>
        <script>
            function toggleSuite(id) {{
                const suite = document.getElementById(id);
                suite.style.display = suite.style.display === 'block' ? 'none' : 'block';
            }}
            function showReport(id) {{
                document.querySelectorAll('.report-section').forEach(el => el.classList.add('hidden'));
                document.getElementById(id).classList.remove('hidden');
            }}
            function filterByStatus(status) {{
                const sections = document.querySelectorAll('.report-section');
                sections.forEach(section => {{
                    const hasStatus = section.getAttribute('data-statuses').includes(status);
                    if (status === 'all' || hasStatus) {{
                        section.classList.remove('hidden');
                        const rows = section.querySelectorAll('table tr');
                        rows.forEach((row, idx) => {{
                            row.style.display = idx === 0 || status === 'all' || row.classList.contains(status) ? '' : 'none';
                        }});
                    }} else {{
                        section.classList.add('hidden');
                    }}
                }});
            }}
            function filterSuite(sectionId, status) {{
                const section = document.getElementById(sectionId);
                const rows = section.querySelectorAll('table tr');
                rows.forEach((row, idx) => {{
                    row.style.display = idx === 0 || status === 'all' || row.classList.contains(status) ? '' : 'none';
                }});
            }}
        </script>
    </head>
    <body>
        {generate_sidebar()}
        <div class="content">
            <h2 align="center">{report_title}</h2>
            <h3 align="center">Runner-Version: {runner_version}</h3>
            <p align="center">Generated on: {timestamp}</p>
            {generate_test_sections()}
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_template)

    print(f"✅ Enhanced report generated: {output_file}")


# Example Usage with Sample Data
test_suites = {
    "Regression Suite": [
        ("1.0", [
            {"test_name": "Login Test", "status": "Passed", "execution_time": "2.1", "expected_results": "Success",
             "actual_results": "Success", "remarks": "OK"},
            {"test_name": "Logout Test", "status": "Passed", "execution_time": "1.5", "expected_results": "Success",
             "actual_results": "Success", "remarks": "OK"}
        ]),
        ("2.0", [
            {"test_name": "Signup Test", "status": "Failed", "execution_time": "3.5",
             "expected_results": "Validation error", "actual_results": "Unexpected error", "remarks": "Bug"},
            {"test_name": "Password Reset Test", "status": "Skipped", "execution_time": "N/A",
             "expected_results": "Reset email sent", "actual_results": "N/A", "remarks": "Not implemented"}
        ])
    ],
    "Smoke Tests": [
        ("1.1", [
            {"test_name": "Cart Test", "status": "Passed", "execution_time": "1.8", "expected_results": "Item added",
             "actual_results": "Item addedReset email sentReset email sentReset email sent,Reset email sentReset email sentReset email sent,Reset email sentReset email sent", "remarks": "Success"}
        ])
    ]
}

# Generate the report
generate_html_report(test_suites)
