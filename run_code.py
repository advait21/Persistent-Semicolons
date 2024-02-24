import requests
from bs4 import BeautifulSoup
from rake_nltk import Rake
import re

def fetch_news(api_key, keyword):
    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}&sortBy=popularity,publishedAt&pageSize=5"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "status" in data and data["status"] == "error":
            print("Error:", data["message"])
            return

        articles = data.get("articles", [])
        if not articles:
            print("No articles found for the keyword:", keyword)
            return

        # Initialize a set to store keywords
        unique_keywords = set()

        for article in articles:
            title = article.get("title", "N/A")
            publication_date = article.get("publishedAt", "N/A")  # Use 'publishedAt' field for publication date
            content = fetch_article_content(article.get("url", ""))  # Fetch full content of the article
            
            if content is None:
                continue

            print("Title:", title)
            print("Publication Date:", publication_date)
            print("Content Length:", len(content))  # Check content length

            # Generate keywords using RAKE
            keywords = generate_keywords(content)

            # Filter out keywords that have already been extracted
            unique_keywords.update(set(keywords) - unique_keywords)

            print("Keywords:", keywords)

            print("\n" + "-"*50 + "\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Error occurred: {e}")

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract text from the article HTML
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        # Clean the text by removing special characters and extra whitespaces
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return cleaned_text
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching content: {http_err}")
        return None
    except Exception as e:
        print(f"Error occurred while fetching content: {e}")
        return None

def generate_keywords(content):
    # Initialize RAKE
    rake = Rake()

    # Extract keywords
    rake.extract_keywords_from_text(content)

    # Get the top 5 keywords
    keywords = rake.get_ranked_phrases()[:5]

    return keywords

def main():
    api_key = "ENTER_API_KEY"
    keyword = input("Enter a keyword: ")
    fetch_news(api_key, keyword)

if __name__ == "__main__":
    main()