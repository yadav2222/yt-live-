import json, random
from moviepy.editor import *
from PIL import Image, ImageDraw

def get_question():
    data = json.load(open("gk.json", encoding="utf-8"))
    return random.choice(data)

def create_image(text, file):
    img = Image.new('RGB', (720,1280), color=(0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((50,200), text, fill=(255,255,255))
    img.save(file)

def make_video():
    q = get_question()

    q_text = f"{q['q']}\n\nA) {q['options'][0]}\nB) {q['options'][1]}\nC) {q['options'][2]}\nD) {q['options'][3]}"
    a_text = f"सही उत्तर: {q['ans']}"

    create_image(q_text, "q.png")
    create_image(a_text, "a.png")

    clip1 = ImageClip("q.png").set_duration(5)
    clip2 = ImageClip("a.png").set_duration(3)

    final = concatenate_videoclips([clip1, clip2])
    final.write_videofile("final.mp4", fps=24)

make_video()
