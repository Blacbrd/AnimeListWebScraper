from playwright.sync_api import sync_playwright
import json

def main():
    # Prompt for the MyAnimeList username
    username = input("Enter MyAnimeList username: ")
    url = f"https://myanimelist.net/animelist/{username}"

    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the user's anime list page
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait for the element that contains the JSON to be present.
        try:
            page.wait_for_selector("div.list-block div.list-unit.all_anime table[data-items]", timeout=15000)
        except Exception as e:
            print("The required element was not found on the page. Check the username or the page structure.")
            browser.close()
            return

        # Locate the table element with the 'data-items' attribute.
        table = page.query_selector("div.list-block div.list-unit.all_anime table[data-items]")
        if not table:
            print("Could not locate the table with the 'data-items' attribute.")
            browser.close()
            return

        data_items = table.get_attribute("data-items")
        if not data_items:
            print("The 'data-items' attribute is empty.")
            browser.close()
            return

        # Parse the JSON from the 'data-items' attribute.
        try:
            anime_list = json.loads(data_items)
        except json.JSONDecodeError as e:
            print("Failed to decode JSON from 'data-items':", e)
            browser.close()
            return

        # Process each anime entry.
        output = []
        for anime in anime_list:
            # Extract the original anime title.
            anime_title = anime.get("anime_title", "")
            # Extract the English title; if missing, use "null".
            anime_title_eng = anime.get("anime_title_eng") or "null"
            
            # Process genres by extracting the "name" from each inner dictionary.
            genres_data = anime.get("genres", [])
            if isinstance(genres_data, list):
                genres = [genre.get("name", "") for genre in genres_data if isinstance(genre, dict)]
                genres_str = ", ".join(genres)
            else:
                genres_str = str(genres_data)
            
            # Extract the start and end dates.
            start_date = anime.get("anime_start_date_string", "")
            end_date = anime.get("anime_end_date_string", "")
            
            # Append the data in the desired format.
            output.append([anime_title, anime_title_eng, genres_str, start_date, end_date])

        # Output the final array of anime entries.
        print("Extracted anime entries:")
        for entry in output:
            print(entry)

        browser.close()

if __name__ == '__main__':
    main()
