import os
import requests
from bs4 import BeautifulSoup
from boilerpy3 import extractors
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

# Collect relevant top stories -> SummarizeNews
class ArticleScrapper:
    
    def __init__(self, base_url) -> None:
        self.topStories = None
        self.latestStories = None
        self.all_ground_news_links = None
        self.article_links = []
        self.all_news_content = []
        self.base_url = base_url
        self.request = requests.get(self.base_url + '/interest/international')
        self.soup = BeautifulSoup(self.request.content, 'html.parser')
        self.extractor = extractors.ArticleExtractor()

        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket('neutralnews-audio-bucket')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

    def getTopStories(self):
        a_tags = self.soup.find_all('a', {'class': 'flex flex-row tablet:flex-col cursor-pointer gap-1_6 w-full'})
        self.topStories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def getLatestStories(self):
        a_tags = self.soup.find_all('a', {'class': 'absolute left-0 right-0 top-0 bottom-0 z-1'})
        self.latestStories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def getArticleLinks(self):
        self.all_ground_news_links = self.topStories + self.latestStories
        for story in self.all_ground_news_links:
            curr_story = requests.get(story)
            curr_soup = BeautifulSoup(curr_story.content, 'html.parser')
            center_article = curr_soup.find('button', string = 'Center')
            try:
                article_link = center_article.find_parent('a')
            except:
                article_link = {'href': None}
            self.article_links.append(article_link['href'])
    
    def logNews(self, arr):
        blob = self.bucket.blob('logs/log_article_scrapping.txt')
        blob.upload_from_string('\n'.join([''.join(str(t)) for t in arr]))


    def getNews(self):
        self.getTopStories()
        self.getLatestStories()
        self.getArticleLinks()

        status_codes = []

        for link in self.article_links:
            try:
                resp = requests.get(link)
                status_codes.append(resp.status_code)
                content = self.extractor.get_content(resp.text)
            except:
                content = None
                status_codes.append(404)
            self.all_news_content.append(content)
        
        all_content = zip(self.all_ground_news_links, self.article_links, self.all_news_content, status_codes)
        filtered_list = [tup for tup in all_content if all(val is not None and val != '' for val in tup)]
        filtered_list = list(filter(lambda x: x[3] == 200, filtered_list))

        self.logNews(filtered_list)

        return filtered_list
