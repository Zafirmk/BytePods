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
from bs4 import BeautifulSoup
from boilerpy3 import extractors
from google.cloud import storage
from dotenv import load_dotenv
from langdetect import detect
load_dotenv()

# Collect relevant top stories -> SummarizeNews
class ArticleScrapper:
    """
    ArticleScrapper object responsible for getting all links.
    """
    def __init__(self, base_url) -> None:
        self.top_stories = None
        self.latest_stories = None
        self.all_ground_news_links = None
        self.article_links = []
        self.headlines = []
        self.all_news_content = []
        self.base_url = base_url
        self.request = requests.get(self.base_url + '/interest/international', timeout=10)
        self.soup = BeautifulSoup(self.request.content, 'html.parser')
        self.extractor = extractors.ArticleExtractor()

        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket(os.getenv('BUCKET_NAME'))
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

    def gettop_stories(self):
        """
        Gets top ground.news article links of top stories.
        """
        a_tags = self.soup.find_all('a', {'class': 'flex flex-row tablet:flex-col cursor-pointer gap-1_6 w-full'})
        self.top_stories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def getlatest_stories(self):
        """
        Gets top ground.news article links of latest stories.
        """
        a_tags = self.soup.find_all('a', {'class': 'absolute left-0 right-0 top-0 bottom-0 z-1'})
        self.latest_stories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def get_headlines(self):
        """
        Gets headlines for all stories.
        """
        self.all_ground_news_links = self.top_stories + self.latest_stories
        for story in self.all_ground_news_links:
            curr_story = requests.get(story, timeout=10)
            curr_soup = BeautifulSoup(curr_story.content, 'html.parser')
            curr_headline = curr_soup.find('h1', {'id': 'titleArticle'})
            try:
                curr_headline = curr_headline.text.strip()
            except:
                curr_headline = None
            self.headlines.append(curr_headline)

    def get_article_links(self):
        """
        Gets article links for all stories.
        """
        self.all_ground_news_links = self.top_stories + self.latest_stories
        for story in self.all_ground_news_links:
            curr_story = requests.get(story, timeout=10)
            curr_soup = BeautifulSoup(curr_story.content, 'html.parser')
            center_article = curr_soup.find('button', string = 'Center')
            try:
                article_link = center_article.find_parent('a')
            except:
                article_link = {'href': None}
            self.article_links.append(article_link['href'])

    def log_news(self, arr):
        """
        Stores logs of the articles scrapped.
        """
        headlines_blob = self.bucket.blob('logs/seen_headlines.txt')
        seen_headlines = headlines_blob.download_as_string().decode()
        for tup in arr:
            headline = tup[5]
            if headline+'\n' not in seen_headlines:
                seen_headlines += (headline+'\n')
        headlines_blob.upload_from_string(seen_headlines)
        blob = self.bucket.blob('logs/log_article_scrapping.txt')
        blob.upload_from_string(','.join([''.join(str(t)) for t in arr]))

    def get_news(self):
        """
        Function to run and get all news reports scrapped.
        """
        self.gettop_stories()
        self.getlatest_stories()
        self.get_article_links()
        self.get_headlines()

        status_codes = []
        languages = []

        for link in self.article_links:
            try:
                if not link: status_codes.append(404)
                resp = requests.get(link)
                content = self.extractor.get_content(resp.text)
                if self.is_english(content):
                    languages.append('en')
                else:
                    languages.append('n/a')
            except:
                content = None
                languages.append('n/a')
            self.all_news_content.append(content)
            if link: status_codes.append(resp.status_code)
        all_content = zip(self.all_ground_news_links, self.article_links, self.all_news_content, status_codes, languages, self.headlines)

        prev_news = self.previous_news()

        filtered_list = [tup for tup in all_content if all(val is not None and val != '' for val in tup)]
        filtered_list = list(filter(lambda x: x[5] not in prev_news, filtered_list))
        filtered_list = list(filter(lambda x: x[3] == 200, filtered_list))
        filtered_list = list(filter(lambda x: x[4] == 'en', filtered_list))

        self.log_news(filtered_list)

        return filtered_list

    def is_english(self, text):
        """
        Checks to see if text is in english.
        """
        try:
            lang = detect(text)
            return bool(lang == 'en')
        except:
            return False

    def previous_news(self):
        """
        Get headlines of news articles previously included.
        """
        prev_headlines = self.bucket.get_blob('logs/seen_headlines.txt').download_as_string().decode().split("\n")
        return prev_headlines
