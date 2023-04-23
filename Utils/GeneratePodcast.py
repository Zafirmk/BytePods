import os
import io
import shutil
import subprocess
from tqdm import tqdm
from datetime import datetime
from pydub import AudioSegment
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.cloud import texttospeech, storage
from googleapiclient.http import MediaIoBaseUpload

load_dotenv()

# Use news summaries and TTS to generate mp3 podcast -> PublishPodcast
class GeneratePodcast:
    
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
        
        self.bucket_name = 'neutralnews-audio-bucket'
        self.bucket_client = storage.Client('TTSCredentials.json')
        self.bucket = self.bucket_client.bucket(self.bucket_name)
        blobs = self.bucket.list_blobs(prefix='individual_summaries/')
        mp3_blobs = [blob for blob in blobs if blob.name.endswith('.mp3')]

        for blob in mp3_blobs:
            blob.delete()

        self.summaries = summaries
        self.gdrive = build('drive', 'v3')
        self.generatePodcast()
    
    def generateTTS(self):
        for idx, summary in tqdm(enumerate(self.summaries)):
            synthesis_input = texttospeech.SynthesisInput(text = summary)
            response = self.tts_client.synthesize_speech(
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )

            blob = self.bucket.blob(f'individual_summaries/output_{idx}.mp3')
            blob.upload_from_string(response.audio_content, content_type = 'audio/mpeg')
            
        self.naturalizeTTS()

    def naturalizeTTS(self):

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
            subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        for filename in sorted(os.listdir('tmp_output')):
            blob = self.bucket.blob(f'individual_summaries/{filename}')
            blob.upload_from_filename(os.path.join('tmp_output', filename), content_type = 'audio/mpeg')
        
        shutil.rmtree('tmp')
        shutil.rmtree('tmp_output')

    def combineTTS(self):

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

        self.savePodcast(mp3_data)

    def savePodcast(self, podcast_mp3):
        # Save to latest episode to GCP bucket & backup on to GDrive
        
        self.bucket.blob("podcast.mp3").upload_from_string(podcast_mp3.getvalue(), content_type = "audio/mpeg")
        self.bucket.blob("podcast.mp3").make_public()

        gdrive_metadata = {'name': f"NewsByte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'parents':['1mCOwiys0019g-cwOqJMMuwzNcgmYPJC3']}
        media = MediaIoBaseUpload(io.BytesIO(self.bucket.blob('podcast.mp3').download_as_bytes()), mimetype='audio/mpeg')
        self.gdrive.files().create(body=gdrive_metadata, media_body=media, fields='id').execute()

    def generatePodcast(self):
        self.generateTTS()
        self.combineTTS()

# Edit so that the GDrive upload is without a service account