import os
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
from google.cloud import texttospeech, storage
from pydub import AudioSegment
import io

# Use news summaries and TTS to generate mp3 podcast -> PublishPodcast
class GeneratePodcast:
    
    def __init__(self) -> None:
        self.tts_client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            name = "en-GB-News-J"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3,
            speaking_rate = 1.25
        )
        self.bucket_name = 'neutralnews-audio-bucket'
        self.bucket_client = storage.Client('TTSCredentials.json')
        self.bucket = self.bucket_client.bucket(self.bucket_name)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
    
    def generateTTS(self, articles):
        for idx, article in tqdm(enumerate(articles)):
            synthesis_input = texttospeech.SynthesisInput(text = article)
            response = self.tts_client.synthesize_speech(
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )

            blob = self.bucket.blob(f'output_{idx}.mp3')
            blob.upload_from_string(response.audio_content, content_type = 'audio/mpeg')

    def combineTTS(self):

        INTRO_DB_REDUCTION = 10
        SEGMENT_CHANGE_DB_REDUCTION = 15
        BACKGROUND_SEGMENT_DB_REDUCTION = 25
        CROSSFADE_DURATION = 500

        news_segment_file_names = [blob.name for blob in self.bucket.list_blobs() if blob.name.startswith('output')]
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

        output_blob = self.bucket.blob("podcast.mp3")
        output_blob.upload_from_string(mp3_data.getvalue(), content_type = "audio/mpeg")