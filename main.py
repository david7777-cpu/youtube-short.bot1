
import os
import asyncio
import time
import requests
from groq import Groq
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

print("=== WORKFLOW STARTED ===")

# 1. Groq AI generates the script using Llama 3.3 (fast & stable)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

script_text = ""
for attempt in range(3):
    try:
        print(f"Attempt {attempt + 1} of 3 to generate script...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": "Create a viral, highly engaging YouTube Short script in English about a mind-blowing psychological or dark historical fact. Max 5 sentences. The first sentence must be an aggressive hook that instantly grabs attention."
                }
            ],
            temperature=0.7,
        )
        script_text = completion.choices[0].message.content.strip()
        break
    except Exception as e:
        print(f"Groq error: {e}. Waiting 5 seconds before retrying...")
        time.sleep(5)

if not script_text:
    raise Exception("Could not retrieve script after 3 attempts.")

print("Script successfully created:", script_text)

# 2. Voice output in English (Edge-TTS)
async def create_voice():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("audio.mp3")
asyncio.run(create_voice())

# 3. Download high-impact background image (Pollinations AI)
img_url = "https://image.pollinations.ai/prompt/dark%20cinematic%20mysterious%20background%20moody%20lighting%204k?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
with open("background.jpg", "wb") as handler:
    handler.write(img_data)

# 4. Assemble video with motion (Cinematic Zoom Effect using MoviePy)
audio_clip = AudioFileClip("audio.mp3")
image_clip = ImageClip("background.jpg").set_duration(audio_clip.duration)
video_clip = image_clip.resize(lambda t: 1 + 0.03 * t)
video = video_clip.set_audio(audio_clip)
video.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("=== VIDEO SUCCESSFULLY COMPLETED ===")
