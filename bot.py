import os, textwrap
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

TOKEN = "8798640307:AAGLZQLZwdPzEMyJ-Se3kyTbt1kDE4iFPdQ"

# ---------- BIG TEXT IMAGE ----------

def create_q_image(question, options, file):
    img = Image.new('RGB', (1080,1920), color=(10,10,10))
    draw = ImageDraw.Draw(img)

    try:
        font_q = ImageFont.truetype("arial.ttf", 80)
        font_o = ImageFont.truetype("arial.ttf", 65)
    except:
        font_q = font_o = None

    # wrap question
    lines = textwrap.wrap(question, width=18)

    y = 150
    for line in lines:
        draw.text((60, y), line, fill=(255,255,255), font=font_q)
        y += 110

    # options
    y += 80
    for i, opt in enumerate(options):
        draw.text((80, y), f"{chr(65+i)}) {opt}", fill=(255,255,0), font=font_o)
        y += 120

    img.save(file)


def create_ans_image(ans, file):
    img = Image.new('RGB', (1080,1920), color=(20,100,20))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 90)
    except:
        font = None

    draw.text((150,800), f"सही उत्तर:\n{ans}", fill=(255,255,255), font=font)

    img.save(file)

# ---------- VOICE ----------

def make_voice(text, file):
    tts = gTTS(text=text, lang='hi')
    tts.save(file)

# ---------- TIMER (BOTTOM) ----------

def timer_clips():
    clips = []
    for i in range(6,0,-1):
        img = Image.new('RGB', (1080,1920), color=(0,0,0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 200)
        except:
            font = None

        draw.text((450,1500), str(i), fill=(255,0,0), font=font)

        name = f"t{i}.png"
        img.save(name)

        clips.append(ImageClip(name).set_duration(1))

    return clips

# ---------- PARSE MULTI QUESTIONS ----------

def parse_questions(text):
    blocks = text.split("Q")
    questions = []

    for b in blocks:
        if not b.strip():
            continue

        lines = b.strip().split("\n")

        q = lines[0].split(":",1)[1].strip()

        opts = []
        ans = ""

        for l in lines:
            if l.startswith("A)"): opts.append(l[2:].strip())
            if l.startswith("B)"): opts.append(l[2:].strip())
            if l.startswith("C)"): opts.append(l[2:].strip())
            if l.startswith("D)"): opts.append(l[2:].strip())
            if l.startswith("ANS"): ans = l.split(":",1)[1].strip()

        questions.append((q, opts, ans))

    return questions

# ---------- VIDEO ----------

def make_video_from_text(raw_text):
    questions = parse_questions(raw_text)

    all_clips = []

    for i, (q, opts, ans) in enumerate(questions):
        create_q_image(q, opts, f"q{i}.png")
        create_ans_image(ans, f"a{i}.png")

        make_voice(q, f"q{i}.mp3")
        make_voice(f"सही उत्तर है {ans}", f"a{i}.mp3")

        q_clip = ImageClip(f"q{i}.png").set_duration(3).set_audio(AudioFileClip(f"q{i}.mp3"))

        timer = concatenate_videoclips(timer_clips())

        a_clip = ImageClip(f"a{i}.png").set_duration(3).set_audio(AudioFileClip(f"a{i}.mp3"))

        all_clips += [q_clip, timer, a_clip]

    final = concatenate_videoclips(all_clips)

    final.write_videofile("final.mp4", fps=24, logger=None)

    return "final.mp4"

# ---------- BOT ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Format bhejo:\n\n"
        "Q1: ...\nA) ...\nB) ...\nC) ...\nD) ...\nANS: ...\n\n"
        "Q2: ..."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video ban raha hai... ⏳")

    video = make_video_from_text(update.message.text)

    await update.message.reply_video(video=open(video, "rb"))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
