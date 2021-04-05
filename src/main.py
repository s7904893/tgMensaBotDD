#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
import telegram as tg
import requests
import json
import os
import io
import time
import logging
from datetime import timedelta
import translate
import random
from bs4 import BeautifulSoup
import praw
import sys

REDDIT_BOT_ID = ''
REDDIT_BOT_SECRET = ''
REDDIT_USER_AGENT = ''
USER_AGENT_BROWSER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
DEEPAI_API_TOKEN = ''

REDDIT_IMAGE_FILE_ENDINGS = [".png", ".jpg", ".jpeg", ".webp"]
REDDIT_VIDEO_SITES = ["youtu.be", "youtube.com", "v.redd.it"]
REDDIT_ANIMATION_FILE_ENDINGS = [".gif"]

royalTitles = ["Lé", "Baron", "König", "Archlord", "Genius", "Ritter", "Curry", "Burger", "Mc", "Doktor",
               "Gentoomaster", "Chef", "Lead Developer", "Sensei"]
firstFrag = ["Schm", "J", "Hans-J", "K", "G", "Gr", "B", "Str", "Kr", "Rask", "Sch"]
secondFrag = ["oerg", "öck", "öhhhrk", "öhrp", "egor", "oeg", "ock", "uck", "orsch"]
thirdFrag = ["inger", "erino", "aroni", "us", "sell", "topus", "thulu", "tain", "rid", "odil", "ette", "nikov", "inus",
             "iborschi"]
nobleAnnex = ["I.", "II.", "III.", "Royale", "dem Allmächtigen", "dem Weisen", "dem hochgradig Intelligenten",
              "dem Unendlichen", "dem Allwissenden", "dem Gentoobändiger", "dem Meisterinformatiker", "dem Meisterkoch",
              "dem Hardwareexperten", "dem Fahrradspitzensportler", "dem Besonnenen", "dem Ausdauernden"]

wisdoms = ["Linux ist voll doof!", "Ich stehe immer um 7.00 Uhr auf!", "Tut schön viel Frischkäse in die Nudelsoße!",
           "Mensen um 11.00 Uhr ist eine super Sache!", "Ich habe WinRar gekauft!",
           "Für einen längeren XP-Supportzeitraum!", "Fasst meinen Laptopbildschirm an!",
           "Natürlich code ich dieses Feature für euch, ganz ohne Pull Request!", "Maxime ist ein toller Papa!",
           "Hirtenkäsepizza ist die beste!", "Sauerkraut ist doch ekelhaft!",
           "Mein Lieblingsbrowser ist ja der Internet Explorer!", "Rechtschreibfehler in Kommentaren? Voll okay!",
           "Party? Warum nicht bei mir zu Hause?", "Irgendwas mit dynamisch Parameter injecten!",
           "Wie war das mit den Speisezeiten?", "Ich kaufe nur bei Nvidia!", "Wer braucht schon Open Source...",
           "KöckOS? Kommt noch diese Woche raus!", "Die besten Witze sind Deine-Mutter-Witze!",
           "Mein Lieblings-OS ist iOS!", "Ein Halloumiburger ist eine eigenständige Mahlzeit!",
           "Ich kaufe mir ein MacBook!", "Ich fange wieder mit Medieninformatik an!", "Ich liebe Ubuntu!",
           "Verschlüsselung ist doch Unsinn!", "Machen wir alle ne gemeinsame WG auf?",
           "Es ist voll in Ordnung, wenn ihr kein Arch Linux benutzt!", "Ich höre am liebsten K.I.Z!",
           "Für Ruhezeiten von 20.00 Uhr bis 5.00 Uhr!", "Ihr seid meine besten Freunde!",
           "Ich entwickele nur noch unter Windows!", "Ich finde Mangas und Animes toll! Schaut mehr Animes!",
           "Ich esse heimlich Schnitzel!"]

haes = ["HÄ?", "APEX?", "OVERWATCH?", "AMONG US?", "WIE", "WANN", "WO", "Geller muss erst noch zu Ende essen!", "???",
        "*Random Katzenbild*", "APEX JETZT!", "ZOCKEN JETZT!", "ICH HASSE EUCH ALLE", "HÄÄÄ", "ICH ARBEITE",
        "ICH HASSE DEN", "FUCK YOU", "WIRKLICH", "BITTE", "Natürlich ist das gelb!", "Es gibt Kuchen!",
        "Wir haben wieder viel zu viel Lasagne!", "Oke", "WAS", "WAS MEINST DU",
        "WAS WILLST DU DENN JETZT SCHON WIEDER", "Alter", "Wirst schon sehen", "Denk nach du Schwamm", "Stop",
        "NICHT COOL", "TROLL NICHT RUM", "Uff", "AAAAARGH", "Kann den jemand kicken?", "DU HAST NUR ANGST VOR MIR",
        "EKELHAFT", "ICH HASSE ALLES", "WOFÜR", "ICH BIN IMMER SO", "KUCHEN", "LASAGNE", "SCHANDE", "WARUM ICH",
        "ICH LIEBE ARBEITEN", "ICH HASSE UNPÜNKTLICHKEIT", "IDIOT", "HEY", "WO SEID IHR", "WAS SONST", "KIBA", "HAHA",
        "VERSTEHT IHR DAS NICHT", "SEID IHR DUMM ODER WAS", "WTF", "RED DEUTSCH MIT MIR", "OMG", "LOL", ":)",
        "MIR IST LANGWEILIG", "ALS OB IHR ALLE SCHON SCHLAFT", "HALLO", "WEIß ICH NICHT", "WER DENKT SICH DAS AUS",
        "ICH SPRING LIEBER AUS DEM FENSTER", "NE", "SCHEISS AUTOKORREKTUR", "ICH BIN NETT", "BONNIIIIIIIIIIIIIEEEE",
        "FICK DICH", "EINE KATZE", "ICH BIN DIE BESTE", "ICH BIN SO DUMM", "*Random Katzenvideo*",
        "ICH KANN EUCH DATINGTIPPS GEBEN", "EH FOREVER", "HENRY <3", "EINE NIELPFERD UWU"]


class NotifyUserException(Exception):
    """Raised whenever an error needs to be propagated to the user"""
    pass


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Reichenbach is never an option!")


def mensa(update, context):
    params = context.args
    if len(params) < 1:
        daysToAdd = 0
    else:
        try:
            daysToAdd = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="The first and only parameter has to be an integer value. Aborting.")
            return
    day = update.message.date.date() + timedelta(days=daysToAdd)
    url = "https://api.studentenwerk-dresden.de/openmensa/v2/canteens/4/days/" + day.strftime("%Y-%m-%d") + "/meals"
    resp = requests.get(url)
    if not resp.ok:
        context.bot.send_message(chat_id=update.message.chat_id, text="I failed miserably. Disgrace!")
        return
    jsonData = json.loads(resp.content)
    for elem in jsonData:
        mealNotes = elem["notes"]
        markdownHighlightChar = "_"
        for note in mealNotes:
            if "vegetarisch" in note or "vegan" in note:
                markdownHighlightChar = "*"

        imgUrl = elem["image"].lstrip(
            "/")  # For some reason, image URLs are prefixed with 2 leading slashes, but no protocol, remove them
        # Do not send placeholder images
        if imgUrl.endswith("studentenwerk-dresden-lieber-mensen-gehen.jpg"):
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=markdownHighlightChar + elem["name"] + markdownHighlightChar,
                                     parse_mode="Markdown")
        else:
            context.bot.send_photo(chat_id=update.message.chat_id, photo=imgUrl,
                                   caption=markdownHighlightChar + elem["name"] + markdownHighlightChar,
                                   parse_mode="Markdown")


def andre(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Höhöhö Reichenbach!")


def leon(update, context):
    joke = dadJoke()
    context.bot.send_message(chat_id=update.message.chat_id, text=joke)


def loen(update, context):
    joke = dadJoke()
    translator = translate.Translator(from_lang='en', to_lang='de')
    translatedJoke = translator.translate(joke)
    context.bot.send_message(chat_id=update.message.chat_id, text=translatedJoke)


def dadJoke():
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://icanhazdadjoke.com/", headers=headers)
    if not resp.ok:
        return "I failed miserably. Disgrace!"
    return resp.text


def georg(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="https://wiki.archlinux.org/index.php/Installation_guide")


def maxime(update, context):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker="CAADBQADfAMAAukKyAPfAAFRgAuYdNoWBA")


def andrey(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="11.00 Bois. Yeef!")


def steffuu(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(haes))


def getXkcd(id, rand):
    resp = requests.get("https://xkcd.com/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")
    jsonData = json.loads(resp.content)
    upperLimit = jsonData["num"]

    if rand:
        id = random.randint(1, upperLimit)
    elif id > upperLimit:
        raise NotifyUserException("Id not in range. Maximum id currently is " + str(upperLimit) + ".")

    resp = requests.get("https://xkcd.com/" + str(id) + "/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")

    jsonData = json.loads(resp.content)
    return (id, jsonData["img"], jsonData["title"])


def xkcd(update, context):
    params = context.args
    rand = False
    id = 0
    if len(params) < 1:
        rand = True
    else:
        try:
            id = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
        if id < 1:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
    try:
        xkcd = getXkcd(id, rand)
    except NotifyUserException as error:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(error))
        return
    context.bot.send_photo(chat_id=update.message.chat_id, photo=xkcd[1], caption=str(xkcd[0]) + " - " + xkcd[2])


def decision(update, context):
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://yesno.wtf/api/", headers=headers)
    if not resp.ok:
        raise NotifyUserException("oof")
    data = json.loads(resp.text)
    context.bot.send_animation(chat_id=update.message.chat_id, animation=data["image"], caption=data["answer"])


def is_video_link(post):
    for video_site in REDDIT_VIDEO_SITES:
        if video_site in post.url:
            return True
    return False


def is_text(post):
    if post.selftext != "":
        return True
    return False


def is_image(post):
    for ending in REDDIT_IMAGE_FILE_ENDINGS:
        if post.url.endswith(ending):
            return True
    return False


def is_animation(post):
    for ending in REDDIT_ANIMATION_FILE_ENDINGS:
        if post.url.endswith(ending):
            return True
    return False


def get_subreddit_images(subreddit, offset=0, count=5):
    images = []
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    for post in reddit.subreddit(subreddit).hot(limit=count):
        if is_image(post):
            images.append(post.url)
    return images


def send_subreddit_posts(subreddit, update, context, offset=0, count=5):
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    posts_sent = False
    try:
        for post in reddit.subreddit(subreddit).hot(limit=count):
            # don't send subreddit rules and such
            if is_text(post) and not post.stickied:
                message = "*" + post.title + "* \n" + post.selftext
                if len(message) > 1000:
                    message = message[:1000]
                    message = message + "*(...)* [" + post.url + "]"
                context.bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.MARKDOWN)
                posts_sent = True
            elif is_video_link(post):
                context.bot.send_message(chat_id=update.message.chat_id, text=post.url)
                posts_sent = True
            elif is_animation(post):
                context.bot.send_animation(chat_id=update.message.chat_id, animation=post.url, caption=post.title)
                posts_sent = True
            elif is_image(post):
                variants = post.preview['images'][0]['variants']
                if "obfuscated" in variants:
                    button = tg.InlineKeyboardButton(text="view", url=post.url)
                    keyboard = tg.InlineKeyboardMarkup([[button]])
                    context.bot.send_photo(chat_id=update.message.chat_id,
                                           photo=variants['obfuscated']['resolutions'][0]['url'], caption=post.title,
                                           reply_markup=keyboard)
                else:
                    context.bot.send_photo(chat_id=update.message.chat_id, photo=post.url, caption=post.title)
                posts_sent = True

    except Exception:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Something went wrong internally. I am deeply sorry.")
        return

    if not posts_sent:
        context.bot.send_message(chat_id=update.message.chat_id, text="No compatible Posts were found.")


def r(update, context):
    params = context.args
    offset = 0
    if len(params) < 1:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="The first parameter has to be a string identifying the requested subreddit. Aborting.")
        return
    subreddit = params[0]
    if len(params) > 1:
        try:
            offset = int(params[1])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="The second parameter has to be a positive integer value. Aborting.")
            return
        if offset < 0:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="The second parameter has to be a positive integer value. Aborting.")
            return

    send_subreddit_posts(subreddit, update, context)


def rr(update, context):
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    sub = reddit.random_subreddit(nsfw=False)
    sub_name = sub.display_name
    context.bot.send_message(chat_id=update.message.chat_id, text="Random subreddit: \"" + sub_name + "\"")
    send_subreddit_posts(sub_name, update, context)


def cat(update, context):
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="https://thiscatdoesnotexist.com?time=" + str(time.time()) + str(random.randint(1, 1024))
    )


def snack(update, context):
    snack = requests.get("https://thissnackdoesnotexist.com/?time=" + str(time.time()) + str(random.randint(1, 1024)),
                         headers={'User-Agent': 'USER_AGENT_BROWSER'})
    if not snack.ok:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Something went wrong internally. I am deeply sorry.")
        return

    soup = BeautifulSoup(snack.text, 'html.parser')
    text = soup.find('h1').text
    pictureUrl = soup.find('div').attrs.get('style').split("(", 1)[1].split(")")[0]
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=pictureUrl,
        caption=text
    )


def horse(update, context):
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="https://thishorsedoesnotexist.com?time=" + str(time.time()) + str(random.randint(1, 1024))
    )


def person(update, context):
    resp = requests.get(
        "https://thispersondoesnotexist.com/image?time=" + str(time.time()) + str(random.randint(1, 1024)),
        headers={'User-Agent': 'USER_AGENT_BROWSER'})

    if not resp.ok:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Something went wrong internally. I am deeply sorry.")
        return

    with io.BytesIO(resp.content) as buf:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=buf)


def wisdom(update, context):
    wisdom = createWisdomString()
    context.bot.send_message(chat_id=update.message.chat_id, text=wisdom)


def createWisdomString():
    optionalNoble = None
    optionalThird = None
    optionalAnnex = None

    if bool(random.getrandbits(1)):
        optionalNoble = random.choice(royalTitles)
    if bool(random.getrandbits(1)):
        optionalThird = random.choice(thirdFrag)
    if bool(random.getrandbits(1)):
        optionalAnnex = random.choice(nobleAnnex)

    mainBody = random.choice(firstFrag) + random.choice(secondFrag)
    output = "Die heutige Weisheit von "

    if optionalNoble:
        output += optionalNoble + " " + mainBody
    else:
        output += mainBody
    if optionalThird:
        output += optionalThird
    if optionalAnnex:
        output += " " + optionalAnnex
    output += ": " + random.choice(wisdoms)
    return output


def choose(update, context):
    params = context.args

    if len(params) < 1:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="You know, I can't choose if there is nothing to choose from. Wise words!")
        return
    elif len(params) == 1:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="How the hell am I supposed to choose when only value is entered? Gosh.")
        return
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(params) + " shall be my answer!")


def inlineR(update, context):
    query = update.inline_query.query
    results = []
    try:
        images = get_subreddit_images(query, count=40)
    except Exception:
        results.append(tg.InlineQueryResultArticle(0, "No", tg.InputTextMessageContent("No!")))
    else:
        if len(images) == 0:
            results.append(tg.InlineQueryResultArticle(0, "No", "No!", ))
        else:
            for img in images:
                results.append(tg.InlineQueryResultPhoto(img, img, img))
    finally:
        update.inline_query.answer(results)


def text_gen(update, context):
    start_text = " ".join(context.args)
    print(start_text)
    response = requests.post("https://api.deepai.org/api/text-generator",
                             data={
                                 'text': start_text,
                             },
                             headers={'api-key': DEEPAI_API_TOKEN}
                             )
    json_response = response.json()
    print(json_response)
    result = "<b>"+start_text+"</b>"+json_response['output'].split(start_text)[1]
    context.bot.send_message(chat_id=update.message.chat_id, text=result,  parse_mode=tg.ParseMode.HTML)


def main():
    polling_enable = False
    reddit_enable = True
    deepai_enable = True

    for i, arg in enumerate(sys.argv):
        if arg == "-p" or arg == "--poll":
            polling_enable = True
        if arg == "--no-reddit":
            reddit_enable = False
        if arg == "--no-deepai":
            deepai_enable = False

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    API_TOKEN = os.environ['TELEGRAM_APITOKEN']
    updater = Updater(token=API_TOKEN, use_context=True)

    startHandler = CommandHandler('start', start)
    updater.dispatcher.add_handler(startHandler)

    mensaHandler = CommandHandler('mensa', mensa)
    updater.dispatcher.add_handler(mensaHandler)

    andreHandler = CommandHandler('andre', andre)
    updater.dispatcher.add_handler(andreHandler)

    leonHandler = CommandHandler('leon', leon)
    updater.dispatcher.add_handler(leonHandler)

    georgHandler = CommandHandler('georg', georg)
    updater.dispatcher.add_handler(georgHandler)

    loenHandler = CommandHandler('loen', loen)
    updater.dispatcher.add_handler(loenHandler)

    maximeHandler = CommandHandler('maxime', maxime)
    updater.dispatcher.add_handler(maximeHandler)

    andreyHandler = CommandHandler('andrey', andrey)
    updater.dispatcher.add_handler(andreyHandler)

    steffuuHandler = CommandHandler('steffuu', steffuu)
    updater.dispatcher.add_handler(steffuuHandler)

    xkcdHandler = CommandHandler('xkcd', xkcd)
    updater.dispatcher.add_handler(xkcdHandler)

    decisionHandler = CommandHandler('decision', decision)
    updater.dispatcher.add_handler(decisionHandler)

    catHandler = CommandHandler('cat', cat)
    updater.dispatcher.add_handler(catHandler)

    snackHandler = CommandHandler('snack', snack)
    updater.dispatcher.add_handler(snackHandler)

    horseHandler = CommandHandler('horse', horse)
    updater.dispatcher.add_handler(horseHandler)

    personHandler = CommandHandler('person', person)
    updater.dispatcher.add_handler(personHandler)

    wisdomHandler = CommandHandler('wisdom', wisdom)
    updater.dispatcher.add_handler(wisdomHandler)

    chooseHandler = CommandHandler('choose', choose)
    updater.dispatcher.add_handler(chooseHandler)

    if deepai_enable:
        global DEEPAI_API_TOKEN
        DEEPAI_API_TOKEN= os.environ['DEEPAI_API_TOKEN']

        continueHandler = CommandHandler('continue', text_gen)
        updater.dispatcher.add_handler(continueHandler)

    if reddit_enable:
        global REDDIT_BOT_ID
        REDDIT_BOT_ID = os.environ['REDDIT_BOT_ID']

        global REDDIT_BOT_SECRET
        REDDIT_BOT_SECRET = os.environ['REDDIT_BOT_SECRET']

        global REDDIT_USER_AGENT
        REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

        redditImgHandler = CommandHandler('r', r)
        updater.dispatcher.add_handler(redditImgHandler)

        redditRandomHandler = CommandHandler('rr', rr)
        updater.dispatcher.add_handler(redditRandomHandler)

        inlineRedditHandler = InlineQueryHandler(inlineR)
        updater.dispatcher.add_handler(inlineRedditHandler)

    if polling_enable:
        updater.start_polling()
        updater.idle()

    else:
        APP_ADDR = os.environ['APP_ADDRESS']
        PORT = int(os.environ.get('PORT', '8443'))
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=API_TOKEN)
        updater.bot.set_webhook(APP_ADDR + API_TOKEN)
        updater.idle()


if __name__ == "__main__":
    main()
