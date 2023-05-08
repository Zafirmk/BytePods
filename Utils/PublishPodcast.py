# pylint: disable=C0301
# pylint: disable=R0902
# pylint: disable=W0702
# pylint: disable=C0103
"""
PodGen implementation to generate RSS feed for podcast.
"""
import os
from datetime import datetime
import feedparser
import pytz
from podgen import Podcast, Episode, Media, Category, Person
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'

# Publish the generated mp3 podcast file
class PublishPodcast:
    """
    PublishPodcast object responsible for publishing podcast episode.
    """
    def __init__(self, episode_name) -> None:
        self.bucket = storage.Client.from_service_account_json('TTSCredentials.json').bucket(os.getenv('BUCKET_NAME'))
        temp = self.bucket.blob('NewsByte_RSS.xml')
        temp.reload()
        self.podcast_xml = feedparser.parse(temp.download_as_string())
        self.episode_name = episode_name
        self.time_zone = pytz.timezone('America/New_York')

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

        self.add_new_episode()
        rss_string = self.podcast.rss_str()
        rss_string = self.insert_extra_tags(rss_string)

        self.bucket.blob('NewsByte_RSS.xml').cache_control = 'public, max-age=60'
        self.bucket.blob('NewsByte_RSS.xml').patch()
        self.bucket.blob('NewsByte_RSS.xml').upload_from_string(rss_string, content_type='application/xml')
        self.bucket.blob('NewsByte_RSS.xml').make_public()

    def insert_extra_tags(self, rss_string):
        """
        Add essential XML tags not included in podgen.
        """
        index = rss_string.find('<item>')
        return rss_string[:index] + '<itunes:type>episodic</itunes:type>\n' + rss_string[index:]

    def get_episode_meta_data(self):
        """
        Get media meta data for current episode
        """
        for blob in self.bucket.list_blobs(prefix = 'podcasts/'):
            if blob.name.split('/')[1] == self.episode_name:
                return (blob.public_url, blob.size)
        return None

    def add_new_episode(self):
        """
        Add new episode into self.podcast object
        """
        meta_data = self.get_episode_meta_data()
        self.podcast.episodes += [
            Episode(
                title = self.episode_name[:-4],
                media = Media(meta_data[0], size = meta_data[1]),
                subtitle = self.bucket.blob('podcast_contents/description.txt').download_as_string().decode(),
                summary = self.bucket.blob('podcast_contents/description.txt').download_as_string().decode(),
                publication_date = self.time_zone.fromutc(datetime.utcnow()).strftime('%m/%d/%Y %H:%M:%S %z')
            )
        ]
