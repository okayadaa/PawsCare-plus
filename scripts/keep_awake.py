"""Visit a Streamlit Community Cloud app so it doesn't go to sleep.

If the app is already asleep, click the "Yes, get this app back up!" button
and wait for it to start. Exits with an error if the app fails to wake, so
GitHub emails you about the failed run.
"""

import os
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("STREAMLIT_APP_URL")
WAKE_BUTTON_TEXT = "Yes, get this app back up"


def main() -> None:
    if not APP_URL:
        sys.exit("STREAMLIT_APP_URL is not set. Add it as a repository variable.")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print(f"Visiting {APP_URL}")
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        try:
            wake_button.wait_for(state="visible", timeout=15_000)
        except PlaywrightTimeout:
            print("App is awake. No action needed.")
        else:
            print("App was asleep. Clicking the wake button...")
            wake_button.click()
            try:
                # The button disappears once the app starts booting.
                wake_button.wait_for(state="hidden", timeout=180_000)
            except PlaywrightTimeout:
                browser.close()
                sys.exit("App did not wake up within 3 minutes.")
            print("Wake-up started.")

        # Stay on the page briefly so the visit registers as real traffic.
        page.wait_for_timeout(15_000)
        browser.close()
        print("Done.")


if __name__ == "__main__":
    main()
