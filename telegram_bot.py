from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# ضع التوكن هنا
BOT_TOKEN = "7369080961:AAHkquXWWHwmBLeWd1dapHfLOUSJNHFOykQ"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

video_hosts = ["megamax.me", "uqload", "vidbom", "drive.google", "streamtape", "filelions", "ok.ru"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "مرحباً! 👋\n"
    "للحصول على روابط الحلقات، استخدم الأمر التالي:\n\n"
    "/episode اسم-الأنمي رقم-الحلقة\n\n"
    "✅ مثال:\n"
    "/episode one-piece 1\n\n"
    "📌 ملاحظات:\n"
    "-  تأكد من كتابة اسم الأنمي بشكل صحيح او بنفس اسم موقع anime4up.\n"
    "- استخدم شرطة `-` للفصل بين الكلمات في اسم الأنمي.\n"
    "- لا تضع علامات ترقيم بين الاسم والرقم.\n\n"
    "🎯 أمثلة إضافية:\n"
    "/episode shingeki-no-kyojin-season-2 5\n"
    "/episode naruto-shippuuden 23\n"
    "/episode hunter-x-hunter-2011 1\n"
    "/episode vinland-saga 6\n" 
    "/episode one-piece 112\n"
    )


async def get_episode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("يرجى إرسال اسم الأنمي ورقم الحلقة، مثال:\n/episode one-piece 1")
        return

    anime = "-".join(context.args[:-1])
    episode_number = context.args[-1]

    try:
        episode_num_int = int(episode_number)
    except ValueError:
        await update.message.reply_text("رقم الحلقة غير صحيح، يرجى إدخال رقم صالح.")
        return

    arabic_episode = f"الحلقة-{episode_num_int}"
    encoded_episode = quote(arabic_episode)
    url = f"https://anime4up.rest/episode/{anime}-{encoded_episode}/"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        await update.message.reply_text("❌ لم يتم العثور على الحلقة. تحقق من اسم الأنمي ورقم الحلقة.")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    title_tag = soup.find("h3")
    episode_title = title_tag.text.strip() if title_tag else f"Episode {episode_num_int}"

    video_players = []
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src and any(host in src for host in video_hosts):
            video_players.append(src)

    download_links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        text = a.get_text()
        if "download" in href.lower() or "تحميل" in text:
            download_links.append(href)

    reply_text = f"🎬 *{episode_title}*\n\n"
    if video_players:
        reply_text += "🔗 روابط المشاهدة:\n" + "\n".join(video_players) + "\n\n"
    else:
        reply_text += "⚠️ لا توجد روابط مشاهدة صالحة.\n\n"

    if download_links:
        reply_text += "⬇️ روابط التحميل:\n" + "\n".join(download_links)
    else:
        reply_text += "⚠️ لا توجد روابط تحميل."

    await update.message.reply_text(reply_text, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("episode", get_episode))

    print("Bot is running...")
    app.run_polling()
