from playwright.sync_api import sync_playwright
import time

def scroll_to_bottom(page, max_scrolls=50):
    """
    Repeatedly scrolls to the bottom of the page until the number of anime entries in the
    Completed section stops increasing or until max_scrolls is reached.
    Works in both headless and non-headless mode.
    """
    last_count = 0
    scrolls = 0
    while scrolls < max_scrolls:
        # Use JavaScript to scroll and handle viewport in headless mode
        page.evaluate("""
            () => {
                window.scrollTo(0, document.body.scrollHeight);
                // Force any lazy-loading elements to load
                const scrollEvent = new Event('scroll');
                window.dispatchEvent(scrollEvent);
            }
        """)
        
        # Wait for content to load - slightly longer in headless mode
        time.sleep(3)
        
        # Check if we need to click "Load More" button if it exists
        load_more_button = page.query_selector('button.load-more')
        if load_more_button and load_more_button.is_visible():
            try:
                load_more_button.click()
                time.sleep(2)  # Wait for new content after clicking
            except Exception as e:
                print(f"Couldn't click load more button: {e}")
        
        # Find the Completed section
        completed_section = None
        list_wraps = page.query_selector_all("div.list-wrap")
        for wrap in list_wraps:
            header = wrap.query_selector("h3.section-name")
            if header and header.inner_text().strip() == "Completed":
                completed_section = wrap
                break
        
        if completed_section:
            # Use JavaScript to ensure all entries are in viewport and loaded
            page.evaluate("""
                (section) => {
                    section.scrollIntoView({behavior: 'smooth', block: 'center'});
                }
            """, completed_section)
            
            time.sleep(2)  # Give time for any lazy-loaded content
            
            anime_entries = completed_section.query_selector_all("div.list-entries div.entry.row")
            current_count = len(anime_entries)
            print(f"Scroll {scrolls}: Found {current_count} entries in Completed section")
            
            if current_count == last_count:
                # Try one more time with a longer wait to be sure
                time.sleep(5)
                anime_entries = completed_section.query_selector_all("div.list-entries div.entry.row")
                current_count = len(anime_entries)
                if current_count == last_count:
                    print("No new entries after waiting longer, stopping scrolls")
                    break
            
            last_count = current_count
        else:
            print("Completed section not found yet, continuing to scroll")
            time.sleep(2)
        
        scrolls += 1
    
    return last_count  # Return the final count for validation

def main():
    # Prompt for the AniList username.
    username = input("Enter AniList username: ")
    url = f"https://anilist.co/user/{username}/animelist/Completed"

    with sync_playwright() as p:
        # Set up browser with appropriate viewport for headless mode
        browser = p.chromium.launch(headless=True)
        # Create context with larger viewport to ensure more content loads
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Handle cookie consent or any initial popups if needed
        try:
            cookie_button = page.query_selector('button[aria-label="Accept cookies"]')
            if cookie_button:
                cookie_button.click()
                time.sleep(1)
        except:
            pass
            
        # Wait for the list-wrap sections to load
        try:
            page.wait_for_selector("div.list-wrap", timeout=15000)
        except Exception as e:
            print(f"No list-wrap sections were found on the page: {e}")
            browser.close()
            return

        # Scroll down repeatedly until no new anime entries are loaded
        final_count = scroll_to_bottom(page)
        print(f"Finished scrolling, found {final_count} total entries")

        # Take a screenshot for debugging (optional)
        # page.screenshot(path="anilist_completed.png")

        # Locate the Completed section
        completed_section = None
        list_wraps = page.query_selector_all("div.list-wrap")
        for wrap in list_wraps:
            header = wrap.query_selector("h3.section-name")
            if header and header.inner_text().strip() == "Completed":
                completed_section = wrap
                break

        if not completed_section:
            print("Completed section not found after scrolling.")
            browser.close()
            return

        # Extract all anime entries using JavaScript to ensure complete extraction
        anime_titles = page.evaluate("""
            () => {
                const completedSection = Array.from(document.querySelectorAll('div.list-wrap'))
                    .find(wrap => {
                        const header = wrap.querySelector('h3.section-name');
                        return header && header.textContent.trim() === 'Completed';
                    });
                
                if (!completedSection) return [];
                
                return Array.from(completedSection.querySelectorAll('div.list-entries div.entry.row'))
                    .map(entry => {
                        const titleEl = entry.querySelector('div.title a');
                        return titleEl ? titleEl.textContent.trim() : '';
                    })
                    .filter(title => title.length > 0);
            }
        """)

        browser.close()

        # Output the final list of anime names
        print(f"Extracted {len(anime_titles)} anime names:")
        for anime in anime_titles[:5]:  # Print first 5 for verification
            print(anime)
        
        if len(anime_titles) > 5:
            print(f"... and {len(anime_titles) - 5} more")

        # Append the anime names to the file
        # append_anime_names(anime_titles)

def append_anime_names(anime_names):
    with open(r"AnimeData\everyAnimeName.txt", "a", encoding="utf-8") as file:
        for name in anime_names:
            file.write(name + "\n")

if __name__ == '__main__':
    main()