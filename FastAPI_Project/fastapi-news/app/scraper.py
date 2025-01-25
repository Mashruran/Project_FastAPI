import datetime
import cloudscraper
from bs4 import BeautifulSoup
from .database import SessionLocal
from .crud import create_news
from .schemas import NewsCreate
print(NewsCreate.__module__)  # Should output something like 'your_project.schemas'
# Initialize cloudscraper
scraper = cloudscraper.create_scraper()

def single_news_scraper(url: str):
    
    try:
        # Fetch the page content
        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract publisher details
        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]

        # Extract the title using the updated CSS selector
        title_element = soup.select_one(
            "body > section > div > div:nth-child(2) > div.grid.lg\\:grid-cols-\\[200px_auto_300px\\].gap-6.mb-6 > div:nth-child(2) > div.mb-3 > h1"
        )
        title = title_element.get_text(strip=True) if title_element else "No Title Found"

        # Extract reporter
        reporter_element = soup.select_one("div.text-xl.text-\\[\\#292929\\].mb-2.lg\\:mb-2 > span")
        reporter = reporter_element.get_text(strip=True) if reporter_element else "No Reporter Found"

        # Extract datetime
        datetime_element = soup.find('div', class_='text-sm')
        news_datetime = datetime_element.get_text(strip=True) if datetime_element else "No Date Found"

        # Extract the category from the URL
        category = url.split('/')[-2].capitalize()

        # Extract body
        body_content = soup.find_all('div', class_='block-full_richtext')
        if body_content:
            paragraphs = body_content[0].find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        else:
            content = "No Content Found"

        # Extract images
        images = [img['src'] for img in soup.find_all('img', src=True)]

        # Set current datetime if extraction failed
        news_datetime = datetime.datetime.now()

        print(f"Scraped news from {url}")
        print(f"Title: {title}")
        print(f"Reporter: {reporter}")
        print(f"Date: {news_datetime}")
        print(f"Category: {category}")
        print(f"Images: {images}")

        return NewsCreate(
            publisher_website=publisher_website,
            news_publisher=publisher,
            title=title,
            news_reporter=reporter,
            datetime=news_datetime,
            link=url,
            news_category=category,
            body=content,
            images=images,
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def scrape_and_store_news(url: str, db: SessionLocal):
    # db = SessionLocal()
    news_data = single_news_scraper(url)
    print(news_data)
    inserted_news = ""
    if news_data:
        # print(news_data)
        inserted_news = create_news(db=db, news=news_data)
    # db.close()

    return inserted_news
