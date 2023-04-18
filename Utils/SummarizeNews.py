import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Summarize news articles -> GeneratePodcast
class SummarizeNews:
    
    def __init__(self, articles) -> None:
        self.summaries = []
        self.articles = articles

    def summarizeArticles(self):

        for article in self.articles:
            response = openai.ChatCompletion.create(
                model = 'gpt-3.5-turbo',
                messages = [
                    {"role": "system", "content": "You summarize news articles into a script for a podcast."},
                    {"role": "user", "content": os.getenv('OPENAI_PROMPT') + str(article[2])}
                ],
                temperature = 0.0
            )

            self.summaries.append(response)