import os
import asyncio
import time
import requests
from google import genai
from google.genai.errors import ServerError
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

print("=== WORKFLOW STARTED ===")

# 1. Gemini AI generates the script in English
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

script_text = ""
for attempt in range(3):
    try:
        print(f"Attempt {attempt + 1} of 3 to generate script...")
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Create a short, engaging fact script for a YouTube Short in English (max 5 sentences)."
        )
        script_text = response.text.strip()
        break
    except ServerError as e:
        print(f"Google server busy (503): {e}. Waiting 10 seconds before retrying...")
        time.sleep(10)

if not script_text:
    raise Exception("Could not retrieve script after 3 attempts due to high server load.")

print("Script successfully created:", script_text)

# 2. Voice output in English (Edge-TTS using US English voice)
async def create_voice():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("audio.mp3")
asyncio.run(create_voice())

# 3. Download background image (Pollinations AI)
img_url = f"https://image.pollinations.ai/prompt/dark%20mysterious%20background?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
with open("background.jpg", "wb") as handler:
    handler.write(img_data)

# 4. Assemble video (MoviePy)
audio_clip = AudioFileClip("audio.mp3")
image_clip = ImageClip("background.jpg").set_duration(audio_clip.duration)
video = image_clip.set_audio(audio_clip)
video.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("=== VIDEO SUCCESSFULLY COMPLETED ===")
