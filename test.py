import asyncio
from playwright.async_api import async_playwright

async def log_into_blackboard(username, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://blackboard.kettering.edu/", timeout=5000)

        if await check_logged_in(page):
            return page  # User is already logged in

        await page.wait_for_selector("#loginForm", timeout=1000)

        await page.fill("#inputUserID", username)
        await page.fill("#inputPassword", password)
        await page.click("#loginForm > button")

        try:
            await page.wait_for_selector("#loginForm", state="hidden", timeout=1000)
        except Exception:
            return "Login failed or timeout reached."

        try:
            if await page.is_visible("#agree_button"):
                await page.click("#agree_button")
        except Exception:
            pass  # Cookie button not found or not clickable

        return page  # Return the logged-in page

async def check_logged_in(page):
    try:
        await page.wait_for_selector("#globalNavPageNavArea > table", timeout=1000)
        return True
    except Exception:
        return False

# Example usage
username = "Free8864"
password = "#CFi^F6TTwot2j"

async def main():
    browser_page = await log_into_blackboard(username, password)
    if isinstance(browser_page, str):
        print(browser_page)
    else:
        print("Logged in successfully")
    await browser_page.close()

asyncio.run(main())
