import os
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
from google.cloud import texttospeech

# Use news summaries and TTS to generate mp3 podcast -> PublishPodcast
class GeneratePodcast:
    
    def __init__(self) -> None:
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            name = "en-GB-News-J"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding = texttospeech.AudioEncoding.MP3,
            speaking_rate = 1.25
        )
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'TTSCredentials.json'
    
    def generateTTS(self, articles):
        for idx, article in tqdm(enumerate(articles)):
            synthesis_input = texttospeech.SynthesisInput(text = article)
            response = self.client.synthesize_speech(
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )
            with open(f"Wavenet_125/output_{idx}.mp3", "wb") as out:
                out.write(response.audio_content)
    
    def combineTTS(self):
        pass

    def addBackgroundMusic(self):
        pass
