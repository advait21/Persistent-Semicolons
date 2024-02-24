import requests
from bs4 import BeautifulSoup
from rake_nltk import Rake
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

from langdetect import detect

@app.route('/fetch_news', methods=['GET'])
def fetch_news():
    api_key = "d1b4f3c50af84ed1a96a0eddaf92c940"
    keyword = request.args.get('keyword')  # This line extracts the keyword from the query parameter

    url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}&sortBy=popularity,publishedAt&pageSize=5&language=en"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "status" in data and data["status"] == "error":
            return jsonify({"error": data["message"]})

        articles = data.get("articles", [])
        if not articles:
            return jsonify({"message": f"No articles found for the keyword: {keyword}"})

        result = []

        for article in articles:
            title = article.get("title", "N/A")
            publication_date = article.get("publishedAt", "N/A")  # Use 'publishedAt' field for publication date
            content = fetch_article_content(article.get("url", ""))  # Fetch full content of the article
            
            if content is None:
                continue

            # Detect language of the content
            lang = detect(content)
            if lang != 'en':
                continue  # Skip non-English articles
            
            # Generate keywords using RAKE
            keywords = generate_keywords(content)

            result.append({
                "title": title,
                "publication_date": publication_date,
                "content_length": len(content),
                "content": content,  # Include content in the response
                "keywords": keywords
            })

        return jsonify(result)

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"})
    except Exception as e:
        return jsonify({"error": f"Error occurred: {e}"})


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

if __name__ == "__main__":
    app.run(debug=True)
