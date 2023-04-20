from Utils.ArticleScrapper import ArticleScrapper
from Utils.SummarizeNews import SummarizeNews
from Utils.GeneratePodcast import GeneratePodcast

if __name__ == '__main__':
    news_reports = ArticleScrapper('http://www.ground.news').getNews()
    print('Article Scrapper Done\n')
    summaries = SummarizeNews(news_reports)
    summaries.summarizeArticles()
    print('Summarizer Done\n')
    GeneratePodcast(summaries.getSummaries())
    print('Podcast Generated\n')