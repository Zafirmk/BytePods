# pylint: disable=C0103
"""
Entry point of CryptoBytes pipeline.
"""
from Utils.ArticleScrapper import ArticleScrapper
from Utils.SummarizeNews import SummarizeNews
from Utils.GeneratePodcast import GeneratePodcast
from Utils.PublishPodcast import PublishPodcast

def main():
    """
    Main function that executes the CryptoBytes pipeline.
    """
    news_reports = ArticleScrapper('https://cryptopotato.com/category/crypto-news/').get_news()
    summaries = SummarizeNews(news_reports)
    summaries.summarize_articles()
    summaries.generate_introduction()
    summaries.generate_outro()
    episode_name = GeneratePodcast(summaries.get_summaries()).get_episode_name()
    PublishPodcast(episode_name)
    

if __name__ == '__main__':
    main()
