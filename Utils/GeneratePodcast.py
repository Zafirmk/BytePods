# pylint: disable=C0301
# pylint: disable=R0902
# pylint: disable=W0702
# pylint: disable=R0914
# pylint: disable=C0103
# pylint: disable=W3101
"""
Podcast mp3 generation using PyDub and so-vits-svc
"""
import os
import io
from datetime import datetime
import requests
from tqdm import tqdm
from pydub import AudioSegment
from pydub.effects import normalize
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

# Use news summaries and TTS to generate mp3 podcast -> PublishPodcast
class GeneratePodcast:
    """
    GeneratePodcast object responsible for creating .mp3 file of podcast episode.
    """
    def __init__(self, summaries) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        self.bucket_client = storage.Client('TTSCredentials.json')
        self.bucket = self.bucket_client.bucket(os.getenv('BUCKET_NAME'))
        blobs = self.bucket.list_blobs(prefix='individual_summaries/')
        mp3_blobs = [blob for blob in blobs if blob.name.endswith('.mp3')]

        for blob in mp3_blobs:
            blob.delete()

        self.summaries = summaries
        self.podcast_number = self.bucket.blob('podcast_contents/podcast_number.txt').download_as_string().decode("utf-8").strip()
        self.episode_name = ""

        self.generate_podcast()

    def generate_tts(self):
        """
        ElevenLabs TTS API call for all summaries.
        """
        CHUNK_SIZE = 1024
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['VOICE_ID']}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.environ['ELEVENLABS_KEY']
        }

        for idx, summary in tqdm(enumerate(self.summaries)):
            data = {
                "text": summary,
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(url, json=data, headers=headers)
            mp3_data = io.BytesIO()
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    mp3_data.write(chunk)

            blob = self.bucket.blob(f'individual_summaries/output_{idx}.mp3')
            mp3_data.seek(0)
            blob.upload_from_file(mp3_data, content_type = 'audio/mpeg')

    def combine_tts(self):
        """
        Combine all TTS clips with background audio.
        """
        INTRO_DB_REDUCTION = 25
        SEGMENT_CHANGE_DB_REDUCTION = 15
        BACKGROUND_SEGMENT_DB_REDUCTION = 35
        CROSSFADE_DURATION = 500

        news_segment_file_names = [blob.name for blob in self.bucket.list_blobs(prefix = 'individual_summaries/') if blob.name.endswith('.mp3')]
        news_segments = [AudioSegment.from_file(io.BytesIO(self.bucket.blob(file).download_as_string())) for file in news_segment_file_names]

        intro = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/intro.mp3').download_as_string())) - INTRO_DB_REDUCTION
        segment_change = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/segment_change.mp3').download_as_string())) - SEGMENT_CHANGE_DB_REDUCTION
        first_segment_background = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/first_segment_background.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION
        segment_background = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/segment_background.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION

        output_audio = AudioSegment.silent(len(intro) - (len(intro) - 5500))

        for i, news_segment in enumerate(news_segments):

            news_segment = AudioSegment.from_file(io.BytesIO(self.bucket.blob(f'individual_summaries/output_{i}.mp3').download_as_string()))

            if i == 0:
                output_audio = output_audio.append(AudioSegment.silent(len(news_segment)))
                output_audio = output_audio.overlay(intro, position = 0, loop = False)
                output_audio = output_audio.overlay(news_segment, position = 4750, loop = False)
                output_audio = output_audio.overlay(first_segment_background, position = len(intro), loop = True)
            else:
                curr_segment = news_segment.overlay(segment_background, loop = True)
                curr_segment = curr_segment.append(AudioSegment.silent(duration=150))
                output_audio = output_audio.append(segment_change.append(curr_segment, crossfade = CROSSFADE_DURATION), crossfade = CROSSFADE_DURATION)

        output_audio = output_audio.append(segment_change, crossfade = CROSSFADE_DURATION)
        mp3_data = io.BytesIO()
        output_audio.export(mp3_data, format="mp3")

        self.save_podcast(mp3_data)

    def save_podcast(self, podcast_mp3):
        """
        Save to latest episode to GCP bucket.
        """
        pod_num = ''
        if len(str(self.podcast_number)) == 1:
            pod_num = f'00{self.podcast_number}'
        elif len(str(self.podcast_number)) == 2:
            pod_num = f'0{self.podcast_number}'

        self.episode_name = f"NewsByte: {pod_num} | Global Date: {datetime.today().strftime('%d-%m-%Y')} | Global Week: {datetime.today().isocalendar()[1]}"

        self.bucket.blob(f"podcasts/{self.episode_name}.mp3").upload_from_string(podcast_mp3.getvalue(), content_type = "audio/mpeg")
        self.bucket.blob(f"podcasts/{self.episode_name}.mp3").make_public()

        self.bucket.blob('podcast_contents/podcast_number.txt').upload_from_string(str(int(self.podcast_number) + 1))

    def get_episode_name(self):
        """
        Getter for self.episode_name with type appended.
        """
        return self.episode_name + '.mp3'

    def generate_podcast(self):
        """
        Main function of class called in __init__.
        """
        self.generate_tts()
        self.combine_tts()
