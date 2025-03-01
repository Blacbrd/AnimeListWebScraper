from playwright.sync_api import sync_playwright
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
        # Launch the browser in headless mode.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the user's anime list page.
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait for at least one anime list item to be present.
        try:
            page.wait_for_selector("tbody.list-item", timeout=15000)
        except Exception as e:
            print("The required list items were not found on the page. Check the username or the page structure.")
            browser.close()
            return

        # Scroll down until no new list items are loaded.
        scroll_to_bottom(page)

        # Locate all the tbody elements with class "list-item".
        anime_elements = page.query_selector_all("tbody.list-item")
        if not anime_elements:
            print("No anime list items found.")
            browser.close()
            return

        # Process each list item.
        output = []
        for element in anime_elements:
            # Extract the anime title.
            title_element = element.query_selector("td.data.title.clearfix a.link.sort")
            anime_title = title_element.inner_text().strip() if title_element else ""

            # Extract the genres. There may be multiple or none.
            genre_elements = element.query_selector_all("td.data.genre span a")
            genres = [g.inner_text().strip() for g in genre_elements if g.inner_text().strip()]
            genres_str = "£".join(genres)
            
            # Append in the desired format: [ "Anime name", "Genre£Genre2£Genre3" ]
            output.append([anime_title, genres_str])

        browser.close()

        # Output the final array of anime entries.
        print("Extracted anime entries:")
        for entry in output:
            print(entry)

        # Write anime names and genres to files.
        getAnimeNames(output)
        getAnimeGenres(output)

# Write each anime name to a file.
def getAnimeNames(output):
    with open(r"AnimeData\everyAnimeName.txt", "a", encoding="utf-8") as file:
        for entry in output:
            file.write(str(entry[0]) + "\n")

# Write each genre (split by '£') to another file.
def getAnimeGenres(output):
    with open(r"AnimeData\everyAnimeGenre.txt", "a", encoding="utf-8") as file:
        for entry in output:
            genres_list = entry[1].split("£")
            for genre in genres_list:
                if genre:  # Write only non-empty genres.
                    file.write(genre + "\n")

if __name__ == '__main__':
    main()
