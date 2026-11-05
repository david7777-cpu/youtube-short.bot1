import os
import asyncio
import time
import requests
from groq import Groq
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

print("=== WORKFLOW STARTED ===")

# 1. Groq AI generiert das Skript
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

script_text = ""
for attempt in range(3):
    try:
        print(f"Attempt {attempt + 1} of 3 to generate script...")
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": "Create a viral, highly engaging YouTube Short script in English about a mind-blowing psychological or dark historical fact. Max 5 sentences. The first sentence must be an aggressive hook that instantly grabs attention."
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
        script_text = completion.choices[0].message.content.strip()
        break
    except Exception as e:
        print(f"Groq error: {e}. Waiting 5 seconds before retrying...")
        time.sleep(5)

if not script_text:
    raise Exception("Could not retrieve script after 3 attempts.")

print("Script successfully created:", script_text)

# 2. Sprach-Ausgabe in Englisch (Edge-TTS)
async def create_voice():
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("audio.mp3")
asyncio.run(create_voice())

# 3. Hintergrundbild herunterladen (Pollinations AI)
img_url = "https://image.pollinations.ai/prompt/dark%20cinematic%20mysterious%20background%20moody%20lighting%204k?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
with open("background.jpg", "wb") as handler:
    handler.write(img_data)

# 4. Video zusammenfügen mit sauberem Ken-Burns-Zoom (Gerade Pixelwerte erzwungen)
audio_clip = AudioFileClip("audio.mp3")
base_clip = ImageClip("background.jpg").set_duration(audio_clip.duration)

def zoom_func(get_frame, t):
    frame = get_frame(t)
    h, w, c = frame.shape
    # Sanfter Zoom-Faktor
    zoom = 1 + 0.04 * (t / audio_clip.duration)
    new_h, new_w = int(h * zoom), int(w * zoom)
    
    # Auf gerade Werte runden, damit H.264 das Video nicht verzerrt
    new_h = new_h if new_h % 2 == 0 else new_h + 1
    new_w = new_w if new_w % 2 == 0 else new_w + 1
    
    # Bild vergrößern & zentrieren
    import PIL.Image
    pil_img = PIL.Image.fromarray(frame).resize((new_w, new_h), PIL.Image.BILINEAR)
    import numpy as np
    resized_frame = np.array(pil_img)
    
    # Zuschneiden auf Originalgröße
    top = (new_h - h) // 2
    left = (new_w - w) // 2
    return resized_frame[top:top+h, left:left+w]

video_clip = base_clip.fl(zoom_func)
video = video_clip.set_audio(audio_clip)

video.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("=== VIDEO SUCCESSFULLY COMPLETED ===")
