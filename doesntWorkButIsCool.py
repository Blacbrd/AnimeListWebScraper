import asyncio
import random
import time
from playwright.async_api import async_playwright

BASE_URL = "https://myanimelist.net"

async def get_anime_urls(username):
    """
    Retrieve all anime URLs from the user's anime list with human-like behavior.
    """
    anime_list_url = f"{BASE_URL}/animelist/{username}"
    anime_urls = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to visually confirm behavior
        context = await browser.new_context(user_agent=random_user_agent())
        page = await context.new_page()
        await page.goto(anime_list_url, wait_until="load")

        # Simulate scrolling
        await human_like_scroll(page)

        await page.wait_for_selector(".list-item", timeout=10000)
        links = await page.query_selector_all("a.link.sort")
        for link in links:
            href = await link.get_attribute("href")
            if href:
                anime_urls.append(href)

        await browser.close()
    return anime_urls

async def get_anime_details(username):
    """
    Navigate to each anime page from the user's list and extract details.
    """
    anime_urls = await get_anime_urls(username)
    print(f"Found {len(anime_urls)} anime entries.")

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=random_user_agent())
        page = await context.new_page()

        random.shuffle(anime_urls)  # Randomize order to mimic human browsing

        for anime_url in anime_urls:
            if anime_url.startswith("/"):
                anime_url = BASE_URL + anime_url
            try:
                wait_time = random.uniform(2, 7)  # Random wait between 2-7 seconds
                print(f"Waiting {wait_time:.2f} seconds before visiting {anime_url}")
                await asyncio.sleep(wait_time)

                await page.goto(anime_url, wait_until="load")
                await human_like_scroll(page)

                title = await page.title()
                results.append(title)
                print(f"Scraped: {title}")
            except Exception as e:
                print(f"Error navigating to {anime_url}: {e}")
        await browser.close()
    return results

async def human_like_scroll(page):
    """
    Simulate a human-like scrolling pattern.
    """
    total_scrolls = random.randint(3, 6)  # Randomize scroll count
    for _ in range(total_scrolls):
        scroll_distance = random.randint(200, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await asyncio.sleep(random.uniform(0.5, 2.5))  # Random delay

def random_user_agent():
    """
    Return a random user-agent string.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
    ]
    return random.choice(user_agents)

if __name__ == '__main__':
    username = input("Enter MyAnimeList username: ")
    results = asyncio.run(get_anime_details(username))

    print("\nAnime Details:")
    for detail in results:
        print(detail)
