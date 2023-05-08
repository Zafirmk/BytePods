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

if __name__ == '__main__':
    main()
