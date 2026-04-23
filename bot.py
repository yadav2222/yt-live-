import os, json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

TOKEN = "8798640307:AAGLZQLZwdPzEMyJ-Se3kyTbt1kDE4iFPdQ"   # ← yahan apna token daalo

# ---------- helpers ----------

def create_image(text, file, bg=(0,0,0)):
    img = Image.new('RGB', (1080,1920), color=bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = None
    draw.text((80,300), text, fill=(255,255,255), font=font)
    img.save(file)

def make_voice(text, file):
    tts = gTTS(text=text, lang='hi')
    tts.save(file)

def timer_clips():
    clips = []
    for i in range(6,0,-1):
        img = Image.new('RGB', (1080,1920), color=(0,0,0))
        draw = ImageDraw.Draw(img)
        draw.text((500,800), str(i), fill=(255,0,0))
        name = f"t{i}.png"
        img.save(name)
        clips.append(ImageClip(name).set_duration(1))
    return clips

def make_video_from_text(raw_text):
    """
    Expect format:
    Q: ...
    A) ...
    B) ...
    C) ...
    D) ...
    ANS: ...
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    q = ""
    opts = ["","","",""]
    ans = ""

    for l in lines:
        if l.lower().startswith("q"):
            q = l.split(":",1)[1].strip()
        elif l.upper().startswith("A)"):
            opts[0] = l[2:].strip()
        elif l.upper().startswith("B)"):
            opts[1] = l[2:].strip()
        elif l.upper().startswith("C)"):
            opts[2] = l[2:].strip()
        elif l.upper().startswith("D)"):
            opts[3] = l[2:].strip()
        elif l.lower().startswith("ans"):
            ans = l.split(":",1)[1].strip()

    q_text = f"{q}\n\nA) {opts[0]}\nB) {opts[1]}\nC) {opts[2]}\nD) {opts[3]}"
    a_text = f"सही उत्तर: {ans}"

    create_image(q_text, "q.png")
    create_image(a_text, "a.png", bg=(20,100,20))

    make_voice(f"ध्यान से सुनिए प्रश्न: {q}", "q.mp3")
    make_voice(f"सही उत्तर है {ans}", "a.mp3")

    q_clip = ImageClip("q.png").set_duration(3).set_audio(AudioFileClip("q.mp3"))
    timer = concatenate_videoclips(timer_clips())
    a_clip = ImageClip("a.png").set_duration(3).set_audio(AudioFileClip("a.mp3"))

    final = concatenate_videoclips([q_clip, timer, a_clip])
    final.write_videofile("final.mp4", fps=24, logger=None)

    return "final.mp4"

# ---------- bot handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Format me question bhejo:\n\n"
        "Q: ...\nA) ...\nB) ...\nC) ...\nD) ...\nANS: ..."
    )

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video ban raha hai ⏳")

    path = make_video_from_text(update.message.text)

    await update.message.reply_video(video=open(path, "rb"))

# ---------- run ----------

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

app.run_polling()
