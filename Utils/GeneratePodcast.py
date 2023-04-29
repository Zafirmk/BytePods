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
import shutil
import subprocess
from datetime import datetime
import requests
from tqdm import tqdm
from pydub import AudioSegment
from dotenv import load_dotenv
from google.cloud import texttospeech, storage

load_dotenv()

# Use news summaries and TTS to generate mp3 podcast -> PublishPodcast
class GeneratePodcast:
    """
    GeneratePodcast object responsible for creating .mp3 file of podcast episode.
    """
    def __init__(self, summaries) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        self.tts_client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            name = "en-GB-News-J"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3,
            speaking_rate = 1.15
        )
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
        Google TTS API call for all summaries.
        """
        for idx, summary in tqdm(enumerate(self.summaries)):
            synthesis_input = texttospeech.SynthesisInput(text = summary)
            response = self.tts_client.synthesize_speech(
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )

            blob = self.bucket.blob(f'individual_summaries/output_{idx}.mp3')
            blob.upload_from_string(response.audio_content, content_type = 'audio/mpeg')

        self.naturalize_tts()

    def naturalize_tts(self):
        """
        so-vits-svc CLI command for all TTS responses from Google TTS API.
        """
        self.download_model()

        BASE_CMD = 'svc'
        MODEL_PATH = 'G_58000.pth'
        CONFIG_PATH = 'config.json'
        OUTPUT_PATH = './tmp_output/'

        if not os.path.exists("tmp"):
            os.mkdir("tmp")

        blobs = self.bucket.list_blobs(prefix='individual_summaries/')
        for blob in blobs:
            if blob.name.endswith(".mp3"):
                name = os.path.join("tmp", blob.name.split('/')[1])
                blob.download_to_filename(name)

        if not os.path.exists("tmp_output"):
            os.mkdir("tmp_output")

        for filename in tqdm(sorted(os.listdir('tmp'))):
            cmd_args = [BASE_CMD, 'infer', f'tmp/{filename}', '-m', MODEL_PATH, '-c', CONFIG_PATH, '-o', f'{OUTPUT_PATH}{filename}', '-na']
            subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        for filename in sorted(os.listdir('tmp_output')):
            blob = self.bucket.blob(f'individual_summaries/{filename}')
            blob.upload_from_filename(os.path.join('tmp_output', filename), content_type = 'audio/mpeg')

        shutil.rmtree('tmp')
        shutil.rmtree('tmp_output')
        os.remove(MODEL_PATH)
        os.remove(CONFIG_PATH)

    def combine_tts(self):
        """
        Combine all TTS clips with background audio.
        """
        INTRO_DB_REDUCTION = 10
        SEGMENT_CHANGE_DB_REDUCTION = 15
        BACKGROUND_SEGMENT_DB_REDUCTION = 20
        CROSSFADE_DURATION = 500

        news_segment_file_names = [blob.name for blob in self.bucket.list_blobs(prefix = 'individual_summaries/') if blob.name.endswith('.mp3')]
        news_segments = [AudioSegment.from_file(io.BytesIO(self.bucket.blob(file).download_as_string())) for file in news_segment_file_names]

        intro = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/intro.mp3').download_as_string())) - INTRO_DB_REDUCTION
        segment_change = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/segment_change.mp3').download_as_string())) - SEGMENT_CHANGE_DB_REDUCTION
        first_segment_background = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/first_segment_background.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION
        segment_background = AudioSegment.from_file(io.BytesIO(self.bucket.blob('fixed_audio_files/segment_background.mp3').download_as_string())) - BACKGROUND_SEGMENT_DB_REDUCTION

        output_audio = intro.fade_out(CROSSFADE_DURATION)

        for i, news_segment in enumerate(news_segments):

            if i == 0:
                curr_segment = news_segment.overlay(first_segment_background, loop = True)
                curr_segment = curr_segment.append(AudioSegment.silent(duration=250))
                output_audio = output_audio.append(curr_segment)
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

    def download_model(self):
        """
        Download the so-vits-model
        """
        url = os.environ['MODEL_URL']
        filename = 'G_58000.pth'
        res = requests.get(url)
        with open(filename, "wb") as f:
            f.write(res.content)

        url = os.environ['MODEL_CONFIG']
        filename = 'config.json'
        res = requests.get(url)
        with open(filename, "wb") as f:
            f.write(res.content)

    def generate_podcast(self):
        """
        Main function of class called in __init__.
        """
        self.generate_tts()
        self.combine_tts()
