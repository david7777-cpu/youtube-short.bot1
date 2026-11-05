import os
import asyncio
import requests
from google import genai
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

print("=== WORKFLOW GESTARTET ===")

# 1. Gemini AI generiert das Skript mit dem aktuellen Modell
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Erstelle ein kurzes, spannendes Fakt-Skript für ein YouTube Short auf Deutsch (max 3 Sätze)."
)
script_text = response.text.strip()
print("Skript erstellt:", script_text)

# 2. Sprach-Ausgabe (Edge-TTS)
async def create_voice():
    communicate = edge_tts.Communicate(script_text, "de-DE-ConradNeural")
    await communicate.save("audio.mp3")
asyncio.run(create_voice())

# 3. Hintergrundbild holen (Pollinations AI - völlig kostenlos)
img_url = f"https://image.pollinations.ai/prompt/dark%20mysterious%20background?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
with open("background.jpg", "wb") as handler:
    handler.write(img_data)

# 4. Video zusammenfügen (MoviePy)
audio_clip = AudioFileClip("audio.mp3")
image_clip = ImageClip("background.jpg").set_duration(audio_clip.duration)
video = image_clip.set_audio(audio_clip)
video.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("=== VIDEO ERFOLGREICH FERTIGGESTELLT ===")
