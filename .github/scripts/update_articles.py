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
        response.raise_for_status()
        data = response.json()
        
        print("Full API Response:", json.dumps(data, indent=2))  # Debug full response
        
        articles = []
        if not isinstance(data, dict):
            print(f"Warning: API response is not a dictionary, got {type(data)}")
            return articles
            
        web_data = data.get('web', {})
        if not isinstance(web_data, dict):
            print(f"Warning: 'web' is not a dictionary, got {type(web_data)}")
            return articles
            
        results = web_data.get('results', [])
        if not isinstance(results, list):
            print(f"Warning: 'results' is not a list, got {type(results)}")
            return articles
            
        for result in results:
            if isinstance(result, dict):
                articles.append({
                    'title': str(result.get('title', '')),
                    'description': str(result.get('description', '')),
                    'url': str(result.get('url', ''))
                })
            else:
                print(f"Warning: result is not a dictionary, got {type(result)}")
                
        print(f"Processed {len(articles)} articles")
        print("First article structure:", json.dumps(articles[0] if articles else {}, indent=2))
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        print(f"Response content: {response.text}")  # Debug response content
        return []
    except Exception as e:
        print(f"Unexpected error in fetch_articles: {e}")
        return []

def create_article_page(articles, date_str):
    if not articles:
        print("Warning: No articles provided to create_article_page")
        return f'''
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
            <p>No articles found</p>
        </div>
    </main>
</body>
</html>
'''
        
    try:
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
        for i, article in enumerate(articles):
            try:
                if not isinstance(article, dict):
                    print(f"Warning: article {i} is not a dictionary: {type(article)}")
                    continue
                    
                title = str(article.get('title', 'No Title'))
                description = str(article.get('description', 'No Description'))
                url = str(article.get('url', '#'))
                
                page_content += f'''
            <article class="article-card">
                <h2>{title}</h2>
                <p>{description}</p>
                <a href="{url}" target="_blank">Read More →</a>
            </article>
'''
            except Exception as e:
                print(f"Error processing article {i}: {e}")
                print(f"Article data: {article}")
                continue
                
        page_content += '''
        </div>
    </main>
</body>
</html>
'''
        return page_content
        
    except Exception as e:
        print(f"Error in create_article_page: {e}")
        return f"<html><body><h1>Error creating page: {e}</h1></body></html>"

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
        else:
            print(f"Main: Got {len(articles)} articles")
            print("Main: First article:", json.dumps(articles[0], indent=2))
        
        # Create new article page
        page_content = create_article_page(articles, date_str)
        with open(f'{article_dir}/index.html', 'w') as f:
            f.write(page_content)
        
        # Update main index page with link to new articles
        article_dates = sorted([d for d in os.listdir('articles') if os.path.isdir(f'articles/{d}')], reverse=True)
        update_index_page(article_dates[:5])
        
    except Exception as e:
        print(f"Error in main function: {e}")
        raise

if __name__ == '__main__':
    main()
