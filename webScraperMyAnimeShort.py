from playwright.sync_api import sync_playwright
import json
import time

def scroll_to_bottom(page):
    """Scroll down the page until no new content is loaded."""
    last_height = page.evaluate("document.body.scrollHeight")
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)  # Wait 5 seconds for new content to load.
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def main():
    # Prompt for the MyAnimeList username
    username = input("Enter MyAnimeList username: ")
    url = f"https://myanimelist.net/animelist/{username}?status=2"

    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the user's anime list page
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait for the initial table element that holds the JSON data
        try:
            page.wait_for_selector("div.list-block div.list-unit.completed table[data-items]", timeout=15000)
        except Exception as e:
            print("The required element was not found on the page. Check the username or the page structure.")
            browser.close()
            return

        # Scroll to the bottom repeatedly until no new content loads.
        scroll_to_bottom(page)

        # Locate the table element with the 'data-items' attribute.
        table = page.query_selector("div.list-block div.list-unit.completed table[data-items]")
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
                genres_str = "£".join(genres)
            else:
                genres_str = str(genres_data)
            
            # Extract the start date.
            start_date = anime.get("anime_start_date_string", "")
            
            # Append the data in the desired format.
            output.append([anime_title, anime_title_eng, genres_str, start_date])

        browser.close()

        # Output the final array of anime entries.
        print("Extracted anime entries:")
        for entry in output:
            print(entry)

        getAnimeNames(output)
        getAnimeGenres(output)
        findOldestAnime(output)

# Output all anime names to a file
def getAnimeNames(output):
    with open(r"AnimeData\everyAnimeName.txt", "a", encoding="utf-8") as file:
        for entry in output:
            file.write(str(entry[0]) + "\n")

def getAnimeGenres(output):
    with open(r"AnimeData\everyAnimeGenre.txt", "a", encoding="utf-8") as file:
        for entry in output:
            genres_list = entry[2].split("£")
            for genre in genres_list:
                file.write(genre + "\n")

def findOldestAnime(output):
    import datetime, os

    def parse_date(date_str):
        try:
            month_str, day_str, year_str = date_str.split('-')
            month = int(month_str)
            day = int(day_str)
            year_val = int(year_str)
            full_year = 2000 + year_val if year_val <= 25 else 1900 + year_val
            return datetime.date(full_year, month, day)
        except Exception:
            return None

    current_oldest_date = None
    current_oldest_entry = None
    for entry in output:
        date_str = entry[3]
        if not date_str:
            continue
        entry_date = parse_date(date_str)
        if entry_date is None:
            continue
        if current_oldest_date is None or entry_date < current_oldest_date:
            current_oldest_date = entry_date
            current_oldest_entry = entry

    file_path = r"AnimeData\oldestAnime.txt"
    file_oldest_date = None
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                line = f.read().strip()
                if line:
                    _, file_date_str = line.rsplit(' ', 1)
                    file_oldest_date = parse_date(file_date_str)
        except Exception:
            pass

    if current_oldest_entry:
        if file_oldest_date is None or current_oldest_date < file_oldest_date:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(current_oldest_entry[0]) + " " + current_oldest_entry[3])

if __name__ == '__main__':
    main()
