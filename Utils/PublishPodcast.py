from mutagen.mp3 import MP3
import io
from podgen import Podcast, Episode, Media, Category, Person
import feedparser
import requests
from datetime import datetime
import datetime as dt
import pytz
import os
from google.cloud import storage
from dotenv import load_dotenv
from pydub import AudioSegment
from pprint import pprint
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

# Publish the generated mp3 podcast file
class PublishPodcast:
    def __init__(self, episodeName) -> None:

        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket(os.getenv('BUCKET_NAME'))
        temp = self.bucket.blob('NewsByte_RSS.xml')
        temp.reload()
        self.podcast_xml = feedparser.parse(temp.download_as_string())
        self.episodeName = episodeName
        self.tz = pytz.timezone('America/New_York')

        self.podcast = Podcast(
            name = self.podcast_xml.feed.title,
            description = self.podcast_xml.feed.subtitle,
            website = self.podcast_xml.feed.link,
            explicit = False,
            language = self.podcast_xml.feed.language,
            category = Category(self.podcast_xml.feed.tags[0].term, self.podcast_xml.feed.tags[1].term),
            authors = [Person(self.podcast_xml.feed.publisher_detail.name, self.podcast_xml.feed.publisher_detail.email)],
            owner = Person(self.podcast_xml.feed.publisher_detail.name, self.podcast_xml.feed.publisher_detail.email),
            image = self.podcast_xml.feed.image.href
        )

        for episode in self.podcast_xml.entries:
            self.podcast.episodes += [
                Episode(
                    title = episode.title,
                    media = Media(episode.links[0].href, size = episode.links[0].length, type = episode.links[0].type),
                    subtitle = episode.subtitle,
                    summary = episode.summary,
                    publication_date = episode.published
                )
            ]
        
        self.addNewEpisode()
        rss_string = self.podcast.rss_str()
        rss_string = self.insertExtraTags(rss_string)

        self.bucket.blob('NewsByte_RSS.xml').cache_control = 'public, max-age=60'
        self.bucket.blob('NewsByte_RSS.xml').patch()
        self.bucket.blob('NewsByte_RSS.xml').upload_from_string(rss_string, content_type='application/xml')
        self.bucket.blob('NewsByte_RSS.xml').make_public()
    
    def insertExtraTags(self, rss_string):
        index = rss_string.find('<item>')
        return (rss_string[:index] + '<itunes:type>episodic</itunes:type>\n' + rss_string[index:])


    def getEpisodeMetaData(self):
        for blob in self.bucket.list_blobs(prefix = 'podcasts/'):
            if blob.name.split('/')[1] == self.episodeName:
                # duration = AudioSegment.from_file(io.BytesIO(self.bucket.blob(blob.name).download_as_string()))
                return(blob.public_url, blob.size)
            
    def addNewEpisode(self):
        metaData = self.getEpisodeMetaData()

        self.podcast.episodes += [
            Episode(
                title = self.episodeName[:-4],
                media = Media(metaData[0], size = metaData[1]),
                subtitle = self.bucket.blob('podcast_contents/description.txt').download_as_string().decode(),
                summary = self.bucket.blob('podcast_contents/description.txt').download_as_string().decode(),
                publication_date = self.tz.fromutc(datetime.utcnow()).strftime('%d/%m/%Y %H:%M:%S %z')
            )
        ]