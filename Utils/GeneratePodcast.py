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
        self.bucket = self.bucket_client.bucket(os.getenv('BUCKET_NAME_CB'))
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
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['VOICE_ID_CB']}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.environ['ELEVENLABS_KEY']
        }

        for idx, summary in tqdm(enumerate(self.summaries)):
            data = {
                "text": summary,
                "voice_settings": {
                    "stability": 0,
                    "similarity_boost": 0
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

    def generate_introduction(self):
        """
        ElevenLabs TTS API call for introduction.
        """
        CHUNK_SIZE = 1024
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['VOICE_ID_CB']}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.environ['ELEVENLABS_KEY']
        }

        data = {
            "text": self.bucket.blob('podcast_contents/introduction.txt').download_as_string().decode('utf-8'),
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0
            }
        }

        response = requests.post(url, json=data, headers=headers)
        mp3_data = io.BytesIO()
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                mp3_data.write(chunk)

        blob = self.bucket.blob('individual_summaries/intro_voice.mp3')
        mp3_data.seek(0)
        blob.upload_from_file(mp3_data, content_type = 'audio/mpeg')
    
    def generate_outro(self):
        """
        ElevenLabs TTS API call for outro.
        """
        CHUNK_SIZE = 1024
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.environ['VOICE_ID_CB']}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.environ['ELEVENLABS_KEY']
        }

        data = {
            "text": self.bucket.blob('podcast_contents/outro.txt').download_as_string().decode('utf-8'),
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0
            }
        }

        response = requests.post(url, json=data, headers=headers)
        mp3_data = io.BytesIO()
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                mp3_data.write(chunk)

        blob = self.bucket.blob('individual_summaries/outro_voice.mp3')
        mp3_data.seek(0)
        blob.upload_from_file(mp3_data, content_type = 'audio/mpeg')

    def combine_tts(self):
        """
        Combine all TTS clips with background audio.
        """
        BACKGROUND_SEGMENT_DB_REDUCTION = 25
        CROSSFADE_DURATION = 500

        news_segment_file_names = [blob.name for blob in self.bucket.list_blobs(prefix = 'individual_summaries/output')]
        news_segments = [AudioSegment.from_file(io.BytesIO(self.bucket.blob(file).download_as_string())) for file in news_segment_file_names]

        intro = AudioSegment.from_file(io.BytesIO(self.bucket.blob('individual_summaries/intro_voice.mp3').download_as_string()))
        outro = AudioSegment.from_file(io.BytesIO(self.bucket.blob('individual_summaries/outro_voice.mp3').download_as_string()))
        background = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/background.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION
        jingle = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/jingle.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION

        final_output = jingle + background
        final_output = final_output.overlay(normalize(intro, headroom=-1.5) + AudioSegment.silent(1500), position=len(jingle)+2600)
        pos = len(jingle) + 2600 + len(intro) + 1500

        final_output = final_output.fade(to_gain=+20.0, start = pos-1500, duration=1500)
        final_output = final_output.fade(to_gain=-20.0, start = pos-1500, duration=1500)

        for i, news_segment in enumerate(news_segments):

            news_segment = normalize(AudioSegment.from_file(io.BytesIO(self.bucket.blob(f'individual_summaries/output_{i}.mp3').download_as_string())), headroom=-1.5)
            final_output = final_output.overlay(news_segment, position=pos)
            pos += (len(news_segment) + 1500)
            final_output = final_output.fade(to_gain=+20.0, start = pos-1500, duration=1500)
            final_output = final_output.fade(to_gain=-20.0, start = pos-1500, duration=1500)
        
        final_output = final_output.overlay(normalize(outro, headroom=-1.5), position=pos)
        pos += (len(outro) + 1500)
        final_output = final_output[:pos]
        final_output = final_output.fade_out(3000)
        mp3_data = io.BytesIO()
        final_output.export(mp3_data, format="mp3")
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

        self.episode_name = f"CryptoByte: {pod_num} | Global Date: {datetime.today().strftime('%d-%m-%Y')} | Global Week: {datetime.today().isocalendar()[1]}"

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
        self.generate_introduction()
        self.generate_outro()
        self.combine_tts()
