# main.py
"""
Main entry point for LinkedIn Smart Surf automation.

This script automates the process of browsing LinkedIn profiles, extracting information, and sending connection requests based on profile relevance.

Workflow:
1. Launches a browser session and prompts the user to log in to LinkedIn.
2. Collects a list of profile URLs to visit using `browse_profiles`.
3. Iterates through each profile URL:
   - Visits the profile.
   - Extracts profile information using `extract_profile_info`.
   - Scores the profile with `score_profile` to determine relevance.
   - If relevant, attempts to send a connection request using `send_connect`.
   - Marks profiles as visited to avoid duplicates.
   - (Optional) Can be extended to queue suggested profiles for further exploration.
4. Ensures delays between actions to avoid bot detection.
5. Closes the browser session upon completion.

Modules Used:
- model: Contains logic for scoring profile relevance.
- linkedin_profile: Functions for extracting profile info and sending connection requests.
- BrowserClient: Abstraction for browser automation.
- browse: Logic for collecting initial profile URLs.
"""

from typing import List
from model import score_profile
from linkedin_profile import extract_profile_info, send_connect
from BrowserClient import BrowserClient
from browse import browse_profiles

def main() -> None:
    """
    Main automation routine for LinkedIn profile processing.

    Steps:
    1. Prompts user to log in to LinkedIn in the automated browser window.
    2. Collects a list of profile URLs to visit.
    3. For each profile:
        - Visits the profile URL.
        - Extracts and prints profile information.
        - Scores the profile for relevance.
        - If relevant, attempts to send a connection request.
        - Marks the profile as visited.
        - (Optional) Can be extended to queue suggested profiles.
    4. Waits between actions to reduce risk of bot detection.
    5. Closes the browser session at the end.
    """
    browser = BrowserClient()
    input("Log into LinkedIn in the browser window and press Enter to start scraping...")

    visited: set[str] = set()
    to_visit: List[str] = browse_profiles(browser, True)

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print(f"\nVisiting {url}")
        browser.get(url)
        browser.sleep(5)
        text = extract_profile_info(browser)
        print("--- Extracted Text ---")
        print(text)

        if score_profile(text):
            print("✅ Marked as interesting")
            # Optionally append to a shortlist file or DB
            if send_connect(browser):
                print("Connection request sent!")
            else:
                print("Could not send connection request.")
        else:
            print("❌ Not interesting")

        visited.add(url)
        # Optionally, add new suggested profiles to the queue here if desired
        # suggested = get_suggested_profiles(browser)
        # for s_url in suggested:
        #     if s_url not in visited and s_url not in to_visit:
        #         to_visit.append(s_url)

        browser.sleep(10)  # avoid triggering bot detection

    print("now ending browser session")
    browser.quit()

if __name__ == "__main__":
    main()
