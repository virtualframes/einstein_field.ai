import re
from playwright.sync_api import Page, expect

def test_submission_flow(page: Page):
    page.goto("http://localhost:8000/docs")

    # Find the "POST /submit" button and click it to expand the details
    page.get_by_role("button", name="POST /submit").click()

    # Find the "Try it out" button and click it
    page.get_by_role("button", name="Try it out").click()

    # Fill in the request body
    page.locator('textarea[aria-label="Request body"]').fill('{"text": "Test inflation claim."}')

    # Click the "Execute" button
    page.get_by_role("button", name="Execute").click()

    # Verify that the response code is 200
    expect(page.locator(".responses-header .response-col_status")).to_have_text("200")

    # Verify that the claim appears in the event log
    page.goto("http://localhost:8000/events")
    expect(page.get_by_text("Test inflation claim.")).to_be_visible()
