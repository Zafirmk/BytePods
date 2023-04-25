# pylint: disable=C0103
"""
Entry point of NewsBytes pipeline.
"""
from Utils.ArticleScrapper import ArticleScrapper
from Utils.SummarizeNews import SummarizeNews
from Utils.GeneratePodcast import GeneratePodcast
from Utils.PublishPodcast import PublishPodcast

def main():
    """
    Main function that executes the NewsBytes pipeline.
    """
    news_reports = ArticleScrapper('http://www.ground.news').get_news()
    print('Article Scrapper Done\n')
    summaries = SummarizeNews(news_reports)
    summaries.summarize_articles()
    print('Summarizer Done\n')
    episode_name = GeneratePodcast(summaries.get_summaries()).get_episode_name()
    print('Podcast Generated\n')
    PublishPodcast(episode_name)
    print('Podcast Published\n')

if __name__ == '__main__':
    main()
