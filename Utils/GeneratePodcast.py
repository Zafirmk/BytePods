import os
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
from google.cloud import texttospeech, storage

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
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
    
    def generateTTS(self, articles):
        bucket = self.bucket_client.bucket(self.bucket_name)

        for idx, article in tqdm(enumerate(articles)):
            synthesis_input = texttospeech.SynthesisInput(text = article)
            response = self.tts_client.synthesize_speech(
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )

            blob = bucket.blob(f'output_{idx}.mp3')
            blob.upload_from_string(response.audio_content, content_type = 'audio/mpeg')

    def combineTTS(self):
        pass

    def addBackgroundMusic(self):
        pass
