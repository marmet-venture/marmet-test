import os
import json
import requests
from datetime import datetime
import pytz
import re

def fetch_articles():
    response = requests.get('https://api.search.brave.com/res/v1/web/search',
                          headers={'X-Subscription-Token': os.environ.get('BRAVE_API_KEY')},
                          params={
                              'q': 'artificial intelligence news latest developments',
                              'count': 10
                          })
    data = response.json()
    # Extract and transform the relevant fields from the Brave API response
    articles = []
    if 'web' in data and 'results' in data['web']:
        for result in data['web']['results']:
            articles.append({
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'url': result.get('url', '')
            })
    return articles

def create_article_page(articles, date_str):
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
        page_content += f'''
            <article class="article-card">
                <h2>{article['title']}</h2>
                <p>{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read More →</a>
            </article>
'''
    page_content += '''
        </div>
    </main>
</body>
</html>
'''
    return page_content

def update_index_page(latest_dates):
    with open('index.html', 'r') as f:
        content = f.read()
    # Add archive section if it doesn't exist
    if '<section class="archive">' not in content:
        insert_pos = content.find('</main>')
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

def main():
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
    
    # Create new article page
    page_content = create_article_page(articles, date_str)
    with open(f'{article_dir}/index.html', 'w') as f:
        f.write(page_content)
    
    # Update main index page with link to new articles
    # Get list of all article directories
    article_dates = sorted([d for d in os.listdir('articles') if os.path.isdir(f'articles/{d}')], reverse=True)
    update_index_page(article_dates[:5])  # Show last 5 dates

if __name__ == '__main__':
    main()