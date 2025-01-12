import os
import json
import requests
from datetime import datetime
import pytz
import re

def fetch_articles():
    try:
        response = requests.get('https://api.search.brave.com/res/v1/web/search',
                              headers={'X-Subscription-Token': os.environ.get('BRAVE_API_KEY')},
                              params={
                                  'q': 'artificial intelligence news latest developments',
                                  'count': 10
                              })
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        # Debug print
        print("API Response structure:", json.dumps(data.keys(), indent=2))
        
        # Extract and transform the relevant fields from the Brave API response
        articles = []
        if not data:
            print("Warning: Empty response from API")
            return articles
            
        if 'web' not in data:
            print("Warning: 'web' key not found in response")
            print("Available keys:", list(data.keys()))
            return articles
            
        if 'results' not in data['web']:
            print("Warning: 'results' key not found in web data")
            print("Available keys in web:", list(data['web'].keys()))
            return articles
            
        for result in data['web']['results']:
            print("Processing result:", json.dumps(result.keys(), indent=2))
            articles.append({
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'url': result.get('url', '')
            })
            
        print(f"Processed {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def create_article_page(articles, date_str):
    if not articles:
        print("Warning: No articles provided to create_article_page")
        articles = []  # Ensure articles is at least an empty list
        
    page_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News - {date_str}</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <header>
        <h1>AI News - {date_str}</h1>
        <nav>
            <a href="/index.html">Home</a>
        </nav>
    </header>
    <main class="container">
        <div class="article-grid">
'''    
    for article in articles:
        try:
            page_content += f'''
            <article class="article-card">
                <h2>{article['title']}</h2>
                <p>{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read More →</a>
            </article>
'''
        except Exception as e:
            print(f"Error processing article: {e}")
            print(f"Article data: {article}")
            continue
            
    page_content += '''
        </div>
    </main>
</body>
</html>
'''
    return page_content

def update_index_page(latest_dates):
    try:
        with open('index.html', 'r') as f:
            content = f.read()
        # Add archive section if it doesn't exist
        if '<section class="archive">' not in content:
            insert_pos = content.find('</main>')
            if insert_pos == -1:
                print("Warning: Could not find </main> tag in index.html")
                return
                
            archive_section = '''
            <section class="archive">
                <h2>Article Archives</h2>
                <ul class="archive-list">
    '''        
            for date in latest_dates:
                archive_section += f'''
                    <li><a href="/articles/{date}/index.html">{date}</a></li>'''        
            archive_section += '''
                </ul>
            </section>
    '''
            content = content[:insert_pos] + archive_section + content[insert_pos:]
            with open('index.html', 'w') as f:
                f.write(content)
    except Exception as e:
        print(f"Error updating index page: {e}")

def main():
    try:
        # Create necessary directories
        os.makedirs('articles', exist_ok=True)
        
        # Get current date in UTC
        now = datetime.now(pytz.UTC)
        date_str = now.strftime('%Y-%m-%d-%H')
        
        # Create directory for current date
        article_dir = f'articles/{date_str}'
        os.makedirs(article_dir, exist_ok=True)
        
        # Fetch and save articles
        articles = fetch_articles()
        if not articles:
            print("Warning: No articles fetched")
        
        # Create new article page
        page_content = create_article_page(articles, date_str)
        with open(f'{article_dir}/index.html', 'w') as f:
            f.write(page_content)
        
        # Update main index page with link to new articles
        # Get list of all article directories
        article_dates = sorted([d for d in os.listdir('articles') if os.path.isdir(f'articles/{d}')], reverse=True)
        update_index_page(article_dates[:5])  # Show last 5 dates
        
    except Exception as e:
        print(f"Error in main function: {e}")
        raise  # Re-raise the exception to ensure the script fails if there's an error

if __name__ == '__main__':
    main()