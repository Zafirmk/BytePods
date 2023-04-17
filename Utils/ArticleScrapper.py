import os
import requests
from bs4 import BeautifulSoup

# Collect relevant top stories -> NewsExtractor
class ArticleScrapper:
    
    def __init__(self, base_url) -> None:
        self.topStories = None
        self.latestStories = None
        self.allStories = None
        self.article_links = []
        self.base_url = base_url
        self.request = requests.get(self.base_url + '/interest/international')
        self.soup = BeautifulSoup(self.request.content, 'html.parser')

    def getTopStories(self):
        a_tags = self.soup.find_all('a', {'class': 'flex flex-row tablet:flex-col cursor-pointer gap-1_6 w-full'})
        self.topStories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def getLatestStories(self):
        a_tags = self.soup.find_all('a', {'class': 'absolute left-0 right-0 top-0 bottom-0 z-1'})
        self.latestStories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    def getArticleLinks(self):
        self.allStories = self.topStories + self.latestStories
        for idx, story in enumerate(self.allStories):
            curr_story = requests.get(story)
            curr_soup = BeautifulSoup(curr_story.content, 'html.parser')
            center_article = curr_soup.find('button', string = 'Center')
            
            if center_article:
                article_link = center_article.find_parent('a')
                self.article_links.append(article_link['href'])
            else:
                self.allStories.pop(idx)