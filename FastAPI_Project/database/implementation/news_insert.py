import os
import mysql.connector
from mysql.connector import Error
from db_connection import create_db_connection
import cloudscraper
from bs4 import BeautifulSoup
import re
import datetime
import html5lib


def execute_query(connection, query, data=None):
    """
    Execute a given SQL query on the provided database connection.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    query : str
        The SQL query to execute.
    data : tuple, optional
        The data tuple to pass to the query, for parameterized queries.

    Returns
    -------
    None
    """
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as e:
        print(f"The error '{e}' occurred")


def insert_category(connection, name, description):
    """
    Inserts a new category into the categories table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    name : str
        The name of the category.
    description : str
        The description of the category.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO categories (name, description)
    VALUES (%s, %s)
    """
    data = (name, description)
    execute_query(connection, query, data)


def insert_author(connection, name, email):
    """
    Inserts a new author into the authors table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    name : str
        The name of the author.
    email : str
        The email of the author.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO authors (name, email)
    VALUES (%s, %s)
    """
    data = (name, email)
    execute_query(connection, query, data)


def insert_editor(connection, name, email):
    """
    Inserts a new editor into the editors table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    name : str
        The name of the editor.
    email : str
        The email of the editor.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO editors (name, email)
    VALUES (%s, %s)
    """
    data = (name, email)
    execute_query(connection, query, data)


def insert_news(connection, category_id, author_id, editor_id, datetime, title, body, link):
    """
    Inserts a new news article into the news table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    category_id : int
        The ID of the category.
    author_id : int
        The ID of the author.
    editor_id : int
        The ID of the editor.
    datetime : datetime
        The publication date and time of the news article.
    title : str
        The title of the news article.
    body : str
        The body text of the news article.
    link : str
        The URL link to the full news article.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO news (category_id, author_id, editor_id, datetime, title, body, link)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    data = (category_id, author_id, editor_id, datetime, title, body, link)
    execute_query(connection, query, data)


def insert_image(connection, news_id, image_url):
    """
    Inserts a new image into the images table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    news_id : int
        The ID of the news article associated with the image.
    image_url : str
        The URL of the image.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO images (news_id, image_url)
    VALUES (%s, %s)
    """
    data = (news_id, image_url)
    execute_query(connection, query, data)


def insert_summary(connection, news_id, summary_text):
    """
    Inserts a new summary into the summaries table.

    Parameters
    ----------
    connection : mysql.connector.connection.MySQLConnection
        The connection object to the database.
    news_id : int
        The ID of the news article associated with the summary.
    summary_text : str
        The text of the summary.

    Returns
    -------
    None
    """
    query = """
    INSERT INTO summaries (news_id, summary_text)
    VALUES (%s, %s)
    """
    data = (news_id, summary_text)
    execute_query(connection, query, data)


def scrape_and_insert_categories():
    """
    Scrapes categories from the website and inserts them into the database.

    Returns
    -------
    None
    """
    # Initialize cloudscraper
    scraper = cloudscraper.create_scraper()

    # Base URL
    base_url = "https://dailyamardesh.com"

    # Fetch the webpage
    response = scraper.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the div containing categories
        categories_div = soup.select_one(
            "body > div.mb-10.lg\\:mb-8 > div.wrapper.z-\\[999\\].bg-white > div:nth-child(2) > div > div > div.flex.flex-row.gap-6.overflow-x-scroll.lg\\:overflow-x-visible"
        )
        if categories_div:
            # Extract category elements
            category_elements = categories_div.find_all("a")
            if category_elements:
                # Establish database connection
                connection = create_db_connection()
                if connection is not None:
                    for category in category_elements:
                        # Extract category name
                        category_name = category.get_text(strip=True)
                        # Create a description
                        description = f"{category_name} description"

                        # Insert into the database
                        print(f"Inserting Category: {category_name}, Description: {description}")
                        insert_category(connection, category_name, description)
                else:
                    print("Failed to connect to the database.")
            else:
                print("No categories found inside the specified div.")
        else:
            print("The specified div could not be located on the page.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

def scrape_and_insert_author():
    """
    Scrapes the author name from the website and inserts it into the authors table.

    Returns
    -------
    None
    """
    # Initialize cloudscraper
    scraper = cloudscraper.create_scraper()

    # Base URL
    base_url = "https://dailyamardesh.com"

    # Default email for author
    default_email = "test@example.com"

    # Fetch the webpage
    response = scraper.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the span containing author info
        author_span = soup.select_one(
            "footer > div.flex.border-t.border-gray-300.py-1.lg\\:py-3.justify-center.md\\:justify-start.font-normal.text-center.md\\:text-left > div > div.flex.flex-col.gap-3 > div.flex.font-semibold > span"
        )
        if author_span:
            # Extract the full text
            full_text = author_span.get_text(strip=True)

            # Use regex to extract the author part after 'সম্পাদক ও প্রকাশক, '
            match = re.search(r"সম্পাদক ও প্রকাশক,\s*(.*)", full_text)
            if match:
                author_name = match.group(1)
                print(f"Author Name: {author_name}")

                # Insert author into the database
                connection = create_db_connection()
                if connection is not None:
                    insert_author(connection, author_name, default_email)
                else:
                    print("Failed to connect to the database.")
            else:
                print("Author name not found.")
        else:
            print("The specified span for the author info could not be located.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


def scrape_and_insert_editor():
    """
    Scrapes the editor name from the website and inserts it into the editors table.

    Returns
    -------
    None
    """
    # Initialize cloudscraper
    scraper = cloudscraper.create_scraper()

    # Base URL
    base_url = "https://dailyamardesh.com"

    # Default email for editor
    default_email = "test@example.com"

    # Fetch the webpage
    response = scraper.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the span containing editor info
        editor_span = soup.select_one(
            "footer > div.flex.border-t.border-gray-300.py-1.lg\\:py-3.justify-center.md\\:justify-start.font-normal.text-center.md\\:text-left > div > div.flex.flex-col.gap-3 > div.flex.font-semibold > span"
        )
        if editor_span:
            # Extract the full text
            full_text = editor_span.get_text(strip=True)

            # Use regex to extract the editor part after 'সম্পাদক ও প্রকাশক, '
            match = re.search(r"সম্পাদক ও প্রকাশক,\s*(.*)", full_text)
            if match:
                editor_name = match.group(1)
                print(f"Editor Name: {editor_name}")

                # Insert editor into the database
                connection = create_db_connection()
                if connection is not None:
                    insert_editor(connection, editor_name, default_email)
                else:
                    print("Failed to connect to the database.")
            else:
                print("Editor name not found.")
        else:
            print("The specified span for the editor info could not be located.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

def scrape_and_insert_news():
    """
    Scrapes news articles from the website and inserts them into the database.

    Returns
    -------
    None
    """
    import datetime

    def parse_bengali_date(bengali_date_str):
        # Mapping of Bengali months to English months
        bengali_to_english_months = {
            "জানুয়ারি": "January",
            "ফেব্রুয়ারি": "February",
            "মার্চ": "March",
            "এপ্রিল": "April",
            "মে": "May",
            "জুন": "June",
            "জুলাই": "July",
            "আগস্ট": "August",
            "সেপ্টেম্বর": "September",
            "অক্টোবর": "October",
            "নভেম্বর": "November",
            "ডিসেম্বর": "December",
        }

        # Convert Bengali numbers to English numbers
        bengali_to_english_numbers = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

        try:
            # Split the date string to extract the day, month, and year
            parts = bengali_date_str.split(",")[1].strip().split(" ")
            day = parts[0].translate(bengali_to_english_numbers)
            month = bengali_to_english_months[parts[1]]
            year = parts[2].translate(bengali_to_english_numbers)

            # Construct a datetime object
            date_obj = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Convert to MySQL datetime format
        except Exception as e:
            print(f"Error parsing date: {e}")
            return None

    # Initialize cloudscraper
    scraper = cloudscraper.create_scraper()

    # Base URL and target page
    base_url = "https://dailyamardesh.com"
    url = "https://dailyamardesh.com/national"

    # Default IDs for category, author, and editor
    default_category_id = 4  # Replace with actual category_id from your database
    default_author_id = 2    # Replace with actual author_id from your database
    default_editor_id = 1    # Replace with actual editor_id from your database

    # Fetch the webpage
    response = scraper.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all links using the CSS selector for the articles
        all_cover_articles = soup.select("h2.text-contrast1 > a")

        # Scrape all the articles
        for article in all_cover_articles:
            # Getting the links (relative URLs)
            relative_link = article.get("href")
            full_url = base_url + relative_link

            # Getting the titles
            title = article.get_text()

            # Now, go to the detail view of the article
            article_response = scraper.get(full_url)
            if article_response.status_code == 200:
                soap_sub_article = BeautifulSoup(article_response.content, "html5lib")

                # Get the article content (body of the article)
                body = soap_sub_article.find_all("div", class_="block-full_richtext")
                paragraphs = body[0].find_all("p")

                # Unifying the paragraphs into one final body text
                list_paragraphs = [p.get_text() for p in paragraphs]
                final_body = " ".join(list_paragraphs)

                # Initialize `date_publish_baseline` before checking
                date_publish_baseline = soap_sub_article.find_all("div", class_="text-sm")
                if date_publish_baseline:
                    bengali_date = date_publish_baseline[0].get_text()
                    publish_date = parse_bengali_date(bengali_date)
                else:
                    publish_date = None  # Or use a default value

                # Print article details (for debugging)
                print(f"Inserting news: {title}, Date: {publish_date}")

                # Insert news into the database
                connection = create_db_connection()
                if connection is not None:
                    insert_news(
                        connection,
                        default_category_id,
                        default_author_id,
                        default_editor_id,
                        publish_date,
                        title,
                        final_body,
                        full_url
                    )
                else:
                    print("Failed to connect to the database.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")



# Example usage
if __name__ == "__main__":
    conn = create_db_connection()
    if conn is not None:
        # scrape_and_insert_categories()
        # scrape_and_insert_author()
        # scrape_and_insert_editor()
        scrape_and_insert_news()
        # Example for other tables:
        # insert_author(conn, "John Doe", "test@example.com")
        # insert_editor(conn, "Jane Doe", "editor@example.com")