from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def generate_pdf_report(test_suites, report_title="AMI Test Report(QA)", output_file="qa_test_report.pdf"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_status_color(status):
        """Returns color for status"""
        status_colors = {"pass": colors.lightgreen, "fail": colors.red, "skip": colors.orange}
        return status_colors.get(status.lower(), colors.black)

    def wrap_long_text(text, max_length=15):
        """Inserts soft hyphens into long text to enable wrapping"""
        if len(text) <= max_length:
            return text
        wrapped_text = ""
        for i in range(0, len(text), max_length):
            chunk = text[i:i + max_length]
            wrapped_text += chunk
            if i + max_length < len(text):
                wrapped_text += "-"
        return wrapped_text

    def prepare_table_data(test_results, styles):
        """Prepares the table data with TestNo starting from 1 for each version"""
        table_data = [["TNo", "Test Name", "Status", "Expected", "Actual", "Remarks"]]  # Header row
        test_no = 1  # Reset to 1 for each version

        for test in test_results:
            wrapped_expected_results = wrap_long_text(test["expected_results"], max_length=15)
            wrapped_actual_results = wrap_long_text(test["actual_results"], max_length=15)
            wrapped_remarks = wrap_long_text(test["remarks"], max_length=15)
            row = [
                Paragraph(str(test_no), styles['Normal']),
                Paragraph(test["test_name"], styles['Normal']),
                Paragraph(f"<b>{test['status'].capitalize()}</b>", styles['Normal']),  # Bold status
                Paragraph(wrapped_expected_results, styles['Normal']),
                Paragraph(wrapped_actual_results, styles['Normal']),
                Paragraph(wrapped_remarks, styles['Normal'])
            ]
            table_data.append(row)
            test_no += 1
        return table_data

    def prepare_summary(test_results, styles):
        """Prepares the summary row of pass/fail/skip counts"""
        total = len(test_results)
        passed = sum(1 for test in test_results if test["status"].lower() == "pass")
        failed = sum(1 for test in test_results if test["status"].lower() == "fail")
        skipped = sum(1 for test in test_results if test["status"].lower() == "skip")
        return [
            [
                Paragraph("Pass", styles['Normal']), Paragraph(str(passed), styles['Normal']),
                Paragraph("Fail", styles['Normal']), Paragraph(str(failed), styles['Normal']),
                Paragraph("Skipped", styles['Normal']), Paragraph(str(skipped), styles['Normal']),
                Paragraph("Total", styles['Normal']), Paragraph(str(total), styles['Normal'])
            ]
        ]

    def prepare_overall_summary(test_suites, styles):
        """Prepares overall summary across all suites"""
        total = passed = failed = skipped = 0
        for suite_name, versions in test_suites.items():
            for version, test_results in versions:
                total += len(test_results)
                passed += sum(1 for test in test_results if test["status"].lower() == "pass")
                failed += sum(1 for test in test_results if test["status"].lower() == "fail")
                skipped += sum(1 for test in test_results if test["status"].lower() == "skip")

        return [
            [
                Paragraph("Overall Pass", styles['Normal']), Paragraph(str(passed), styles['Normal']),
                Paragraph("Overall Fail", styles['Normal']), Paragraph(str(failed), styles['Normal']),
                Paragraph("Overall Skipped", styles['Normal']), Paragraph(str(skipped), styles['Normal']),
                Paragraph("Overall Total", styles['Normal']), Paragraph(str(total), styles['Normal'])
            ]
        ]

    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=letter, leftMargin=36, rightMargin=36)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 12
    styles['Normal'].alignment = 1

    # Title Section
    title_text = f"<font size=14><b>{report_title}</b></font><br/><font size=10>{timestamp}</font>"
    title = Paragraph(title_text, styles['Title'])
    elements.append(title)

    # Overall Summary
    overall_summary_data = prepare_overall_summary(test_suites, styles)
    overall_summary_table = Table(overall_summary_data, colWidths=[70, 50, 70, 50, 70, 50, 70, 50])
    overall_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(overall_summary_table)

    # Test suite details
    for suite_name, versions in test_suites.items():
        elements.append(Paragraph(f"<b>Test Suite: {suite_name}</b>", styles['Heading2']))

        for version, test_results in versions:
            elements.append(Paragraph(f"<b>Version: {version}</b>", styles['Heading3']))
            summary_data = prepare_summary(test_results, styles)

            # Summary table
            summary_table = Table(summary_data, colWidths=[60, 40, 60, 40, 60, 40, 60, 40])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(summary_table)

            # Test results table
            table_data = prepare_table_data(test_results, styles)
            table = Table(table_data, colWidths=[25, 100, 50, 100, 150, 175])

            # Dynamic row coloring based on status
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ])

            # Add row-specific background colors
            for i, test in enumerate(test_results, 1):
                status = test["status"].lower()
                bg_color = colors.lightgreen if status == "pass" else \
                    colors.lightcoral if status == "fail" else \
                        colors.lightyellow if status == "skip" else colors.beige
                table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

            table.setStyle(table_style)
            elements.append(table)

    # Build the PDF
    doc.build(elements)
    print(f"PDF report generated successfully: {output_file}")


# Example usage
if __name__ == "__main__":
    test_suites = {
        "Regression Suite": [
            ("1.0", [
                {"test_name": "Login Testfdfgdfgdgdgfdfgdfgdfdf dfgdfgdfgdfgdfg sdfgdfdgdfg", "status": "Pass", "expected_results": "Success",
                 "actual_results": "Success", "remarks": "OK"},
                {"test_name": "Logout Test", "status": "Pass", "expected_results": "Success",
                 "actual_results": "Success", "remarks": "OK"},
                {"test_name": "Long Logout Test", "status": "Pass", "expected_results": "SuccessSuccessSuccessSuccessSuccess SuccessSuccessSuccessSuccessSuccessSuccess",
                 "actual_results": "Success", "remarks": "SuccessSuccessSuccessSuccessSuccessSuccess"}
            ])
        ],
        "Smoke Tests": [
            ("1.1", [
                {"test_name": "Cart Test", "status": "Pass", "expected_results": "Item added",
                 "actual_results": "Item added", "remarks": "Success"},
                {"test_name": "Signup Test", "status": "Fail",
                 "expected_results": "Validation error", "actual_results": "Unexpected erronexpected erronexpected erronexpected erronexpected erronexpected erronexpected erronexpected erronexpected erronexpected error", "remarks": "Bug"},
                {"test_name": "Password Reset Test", "status": "Skip",
                 "expected_results": "Reset email sentReset email sentReset email sent",
                 "actual_results": "N/A", "remarks": "Not implemented"}
            ])
        ]
    }
    generate_pdf_report(test_suites)