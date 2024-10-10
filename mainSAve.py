import openai
import pyaudio
import os
import uuid
from pydub import AudioSegment
from pydub.playback import play
from elevenlabs import VoiceSettings
from elevenlabs import ElevenLabs
import subprocess
import time
import sys
import vlc

# Tilføj VLC-bibliotek sti til systemvej
# Make sure you have vlc installed as it is used to play the voice
vlc_path = "C:/Program Files (x86)/VideoLAN/VLC"
os.environ['PATH'] += os.pathsep + vlc_path

# Indsæt din OpenAI API-nøgle her
openai.api_key = 'YOUR_CHATGPT_KEY_HERE'

# Indsæt din ElevenLabs API-nøgle her
ELEVENLABS_API_KEY = 'YOUR_ELEVENLABS_KEY_HERE'
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


# Funktion til at få AI-svar fra GPT
def gpt_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Funktion til at generere tale med ElevenLabs og gemme som mp3
def text_to_speech_file(text: str) -> str:
    response = client.text_to_speech.convert(
        voice_id="SOYHLrjzK2X1ezoPC6cr",  # Eric stemme-id, du kan ændre dette
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",  # Turbo model for lav latenstid
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    # Gem lydfil med et unikt navn
    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    return save_file_path

# Funktion til at afspille lydfilen
import vlc


def play_audio(file_path):
    # Opret en midlertidig sti i den ønskede temp-mappe
    temp_wav_path = os.path.join("C:/Users/USER/OneDrive/Documents/TTsAI/Audio", "temp_audio.wav")
    
    # Konverter MP3 til WAV og gem i den midlertidige sti
    audio_segment = AudioSegment.from_mp3(file_path)
    audio_segment.export(temp_wav_path, format="wav")
    
    # Brug VLC til at afspille lydfilen
    player = vlc.MediaPlayer(temp_wav_path)
    player.play()

    # Vent indtil lyden begynder at spille
    while player.get_state() not in [vlc.State.Playing, vlc.State.Error]:
        time.sleep(0.1)

    # Vent indtil lyden er færdig med at spille
    while player.get_state() == vlc.State.Playing:
        time.sleep(0.1)

    # Når afspilningen er færdig, slet den midlertidige fil
    try:
        os.remove(temp_wav_path)  # Slet den midlertidige fil
    except Exception as e:
        print(f"Kunne ikke slette filen: {e}")


# Hovedfunktionen, der styrer workflowet
def main():
    # Start samtalehistorikken med en systemmeddelelse
    messages = [
        {"role": "system", "content": "User_input"}
    ]
    
    first_input = True  # Variabel til at holde styr på, om det er første input
    
    while True:
        if first_input:
            user_input = input("INSERT YOUR MESSAGE (Type 'exit' to end the convo): ")
            first_input = False
        else:
            user_input = input(">>>> ")
        
        if user_input.lower() == 'exit':
            print("ENDING CONVO.")
            break
        
        messages.append({"role": "user", "content": user_input})
        ai_response = gpt_response(messages)  
        print("AI response:", ai_response)
        
        audio_file = text_to_speech_file(ai_response)
        play_audio(audio_file)
        
        messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    main()
