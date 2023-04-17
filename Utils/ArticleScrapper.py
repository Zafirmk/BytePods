import os
import requests
from bs4 import BeautifulSoup

# Collect relevant top stories -> NewsExtractor
class ArticleScrapper:
    
    def __init__(self, base_url) -> None:
        self.base_url = base_url
        self.topStories = []
        self.article_links = []
        self.soup = None
        
    def getTopStories(self):
        request = requests.get(self.base_url + '/interest/international')
        self.soup = BeautifulSoup(request.content, 'html.parser')
        a_tags = self.soup.find_all('a', {'class': 'absolute left-0 right-0 top-0 bottom-0 z-1'})
        self.topStories = list(map(lambda toAppend: self.base_url + toAppend, map(lambda a_tag: a_tag['href'], a_tags)))

    # Extract a link for the top stories
    def getArticleLinks(self):
        pass


# obj = ArticleScrapper('https://ground.news')
# obj.getTopStories()

# for story in obj.topStories:
#     print(story)