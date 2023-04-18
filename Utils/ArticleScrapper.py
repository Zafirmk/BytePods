import os
import requests
from bs4 import BeautifulSoup
from boilerpy3 import extractors

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
    
    def getNews(self):
        self.getTopStories()
        self.getLatestStories()
        self.getArticleLinks()

        for link in self.article_links:
            try:
                resp = requests.get(link)
                content = self.extractor.get_content(resp.text)
            except:
                content = None
            self.all_news_content.append(content)
        
        all_content = zip(self.all_ground_news_links, self.article_links, self.all_news_content)
        filtered_list = [t for t in all_content if None not in t]

        return filtered_list
