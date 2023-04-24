from Utils.ArticleScrapper import ArticleScrapper
from Utils.SummarizeNews import SummarizeNews
from Utils.GeneratePodcast import GeneratePodcast
from Utils.PublishPodcast import PublishPodcast
import time

if __name__ == '__main__':
    t0 = time.time()
    news_reports = ArticleScrapper('http://www.ground.news').getNews()
    print('Article Scrapper Done\n')
    summaries = SummarizeNews(news_reports)
    summaries.summarizeArticles()
    print('Summarizer Done\n')
    episode_name = GeneratePodcast(summaries.getSummaries()).getEpisodeName()
    print('Podcast Generated\n')
    PublishPodcast(episode_name)
    print('Podcast Published\n')
    t1 = time.time()

    print(f'\nTime Taken: {t1 - t0}')