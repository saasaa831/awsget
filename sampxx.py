import asyncio
from pyppeteer import launch


async def html_to_pdf(input_html, output_pdf):
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Load HTML content
    html_content = open(input_html, 'r').read()
    await page.setContent(html_content)

    # Wait for page and all frames to load
    await page.waitForSelector('body')  # Wait for body or any other element to be fully loaded

    # Generate the PDF, this will preserve links
    await page.pdf({
        'path': output_pdf,
        'format': 'A4',
        'printBackground': True,
        'displayHeaderFooter': False
    })

    await browser.close()


# Run the function to convert HTML to PDF
asyncio.get_event_loop().run_until_complete(html_to_pdf("qa_test_report.html", "qa_test_reportxxx1.pdf"))