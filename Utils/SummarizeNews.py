import os
import openai
from dotenv import load_dotenv
from tqdm import tqdm
from google.cloud import storage
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Summarize news articles -> GeneratePodcast
class SummarizeNews:
    
    def __init__(self, articles) -> None:
        self.summaries = []
        self.articles = articles
        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket('neutralnews-audio-bucket')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

    def summarizeArticles(self):
        for article in tqdm(self.articles):
            try:
                response = openai.ChatCompletion.create(
                    model = 'gpt-3.5-turbo',
                    messages = [
                        {"role": "system", "content": "You summarize news articles into a script for a podcast."},
                        {"role": "user", "content": os.getenv('OPENAI_PROMPT') + str(article[2])}
                    ],
                    temperature = 0.0
                )
                self.summaries.append(response["choices"][0]["message"]["content"])
            except:
                response = ""
                self.summaries.append("")

        self.summaries = [s for s in self.summaries if s != ""]
        self.logSummaries()
        self.generateDescription()

    def logSummaries(self):
        blob = self.bucket.blob('logs/log_summaries.txt')
        blob.upload_from_string('\n'.join(self.summaries))

    def generateDescription(self):
        headlines = list(map(lambda string: string.split(".")[0], self.summaries[:3]))
        
        try:
            response = openai.ChatCompletion.create(
                model = 'gpt-3.5-turbo',
                messages = [
                    {"role": "system", "content": "You create a description for a podcast."},
                    {"role": "user", "content": os.getenv('OPENAI_DESCRIPTION_PROMPT') + str(headlines[0]) + '\n' + str(headlines[1]) + '\n' + str(headlines[2]) + '\n'}
                ],
                temperature = 0.0
            )

            blob = self.bucket.blob('description.txt')
            blob.upload_from_string(response["choices"][0]["message"]["content"])

        except:
            response = "Welcome to today's episode! Have a nice day ahead!"
            blob = self.bucket.blob('description.txt')
            blob.upload_from_string(response)
            blob.make_public()

    def getSummaries(self):
        return self.summaries