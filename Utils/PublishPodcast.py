from podgen import Podcast, Episode, Media, Category, Person
import datetime
import os
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

# Publish the generated mp3 podcast file
class PublishPodcast:
    def __init__(self) -> None:

        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket('neutralnews-audio-bucket')

        self.podcast = Podcast(
            name = "NewsBytes",
            description = "Stay informed and stay ahead with our daily newsbytes! From breaking headlines to global events, we deliver the news you need to know. Don't have time to sift through endless articles? Let us bring the world to you, in just 5 minutes a day. Tune in and be in the know!",
            website = "https://storage.googleapis.com/neutralnews-audio-bucket/rss.xml",
            explicit = False,
            language = "en-US",
            category = Category("News", "Daily News"),
            authors = [Person("Zafir Khalid", "zafirmk0@gmail.com")],
            owner = Person("Zafir Khalid", "zafirmk0@gmail.com"),
            image = "https://storage.googleapis.com/neutralnews-audio-bucket/podcastlogo.png"
        )
        self.podcast.set_generator('https://simplecast.com', exclude_podgen=True)

        self.podcast_blob = self.bucket.blob('podcast.mp3')
        self.podcast_blob.reload()

        self.podcast_size = self.podcast_blob.size

        self.description = self.bucket.blob('description.txt').download_as_string()
        self.podcast_number = self.bucket.blob('podcast_number.txt').download_as_string().decode("utf-8").strip()

        if (len(str(self.podcast_number)) == 1):
            self.podcast_number = f'00{self.podcast_number}'
        elif (len(str(self.podcast_number)) == 2):
            self.podcast_number = f'0{self.podcast_number}'
            
        self.podcast.episodes += [
            Episode(
                title = f"NewsByte: {self.podcast_number} - Global Date: {datetime.date.today().strftime('%d/%m/%Y')} - Global Week: {datetime.date.today().isocalendar()[1]}",
                media = Media("https://storage.googleapis.com/neutralnews-audio-bucket/podcast.mp3", self.podcast_size),
                subtitle = self.description,
                summary = self.description
            )
        ]

        self.bucket.blob('rss.xml').upload_from_string(self.podcast.rss_str(), content_type='application/xml')
        self.bucket.blob('rss.xml').make_public()

PublishPodcast()