# pylint: disable=C0301
# pylint: disable=R0902
# pylint: disable=W0702
# pylint: disable=C0103
# pylint: disable=C0321
# pylint: disable=W3101
"""
BeautifulSoup scrapper to get articles.
"""
import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from boilerpy3 import extractors
from google.cloud import storage
from dotenv import load_dotenv
from langdetect import detect
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')
load_dotenv()

# Collect relevant top stories -> SummarizeNews
class ArticleScrapper:
    """
    ArticleScrapper object responsible for getting all links.
    """
    def __init__(self, base_url) -> None:
        self.base_url = base_url
        self.latest_stories = []
        self.content = []
        self.request = requests.get(self.base_url, timeout=10)
        self.soup = BeautifulSoup(self.request.content, 'html.parser')
        self.extractor = extractors.ArticleExtractor()
        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket(os.getenv('BUCKET_NAME_CB'))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
    
    def get_latest_stories(self):
        article_soups = self.soup.find_all('article', {'class': 'category-crypto-news'})
        for article_soup in article_soups:
            a_tag = article_soup.find('a')
            time = article_soup.find('time')
            if date.fromisoformat(time['datetime']) == date.today():
                self.latest_stories.append((time['datetime'], a_tag['title'], urljoin(self.base_url, a_tag['href'])))
        self.latest_stories = self.latest_stories[:6]

    def get_news(self):
        self.get_latest_stories()

        for tup in self.latest_stories:
            resp = requests.get(tup[2])
            headline = tup[1]
            content = self.extractor.get_content(resp.text)
            self.content.append((headline, content))
        
        self.update_logs()

        return self.content
    
    def update_logs(self):
        articles = ""

        for tup in self.latest_stories:
            articles += ", ".join(tup) + "\n"

        self.bucket.blob('logs/logs_articles.txt').upload_from_string(articles.encode('utf-8'), content_type='text/plain; charset=utf-8')
