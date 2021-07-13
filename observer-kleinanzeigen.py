# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 11:24:23 2021

@author: Jose A
"""
#Miniscrapper
import requests
import re
from bs4 import BeautifulSoup

#Telegrambot
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

import argparse

anuncioid_db={}
TOKEN=None
URLLIST=[]
MINS=0
MAXS=100000

class Article:
    def __init__(self, title, price, url, date, imageurl, anuncioid):
        self.title = title
        self.price = price
        self.url = 'https://www.ebay-kleinanzeigen.de' + url
        self.date = date
        self.imageurl = imageurl
        self.anuncioid=anuncioid
        
def updateList(url):
    user_agent = {'User-agent': 'Mozilla/5.0'}    
    qq = requests.get(url, headers = user_agent)
    text = qq.text
    soup = BeautifulSoup(text)
    #print(soup.prettify())
    
    articles = soup.find_all("article", {"class": "aditem"}) 
    articles_to_notify=[]
    
    for item in articles:
        anuncioid=item['data-adid']  
        price=item.find("p", {"class": "aditem-main--middle--price"}).text[2::]
        if (anuncioid in anuncioid_db):
            if (anuncioid_db[anuncioid].price == price):
                continue
            
        title=item.find('a',{"class":"ellipsis"}).text
        suburl= item['data-href']
        price=item.find("p", {"class": "aditem-main--middle--price"}).text[2::]
        date= item.find('div',{ "class":"aditem-main--top--right"}).text[2::]
        try:
            imgbox=item.find('div',{"class":"imagebox srpimagebox"})
            image = imgbox['data-imgsrc']
        except Exception as e:
            logger.error('No image in'+suburl)
            continue
        #print (title, price, anuncioid)
        anuncioid_db[anuncioid]=Article(title, price, suburl, date, image, anuncioid)
        articles_to_notify.append(anuncioid_db[anuncioid])

    return articles_to_notify
def randomSleep() -> int:
    return random.randint(MINS, MAXS)
#------------------------TELEGRAM--------------------------------    
msghello="Hello, paste here the new URLs, even when it's running\n. To start write /start. To delete the last item /testdelete"

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def scheduled_update(context: CallbackContext):

    #cycle through the url list
    global URLLIST
    print('URL List')
    print(URLLIST)
    
    try:
        new_items=updateList(URLLIST[0])
    except Exception as e:
        URLLIST.insert(0, URLLIST.pop())
        new_items=updateList(URLLIST[0])
    URLLIST.insert(0, URLLIST.pop())
    
    
    #Send the new items to telegram
    chat_id=context.job.context    
    for new in new_items:
        textitem=f"<b>{new.title}</b>\n{new.price}\n{new.date}\n<a href='{new.url}'>Link</a>\n{new.imageurl}"
        print('sending message')
        context.bot.send_message(chat_id=chat_id, 
                             text=textitem,
                             parse_mode = "HTML")

    #do this again later
    context.job_queue.run_once(scheduled_update, randomSleep(), context=chat_id, name=str(context))


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.user_data["chat_id"]=chat_id
    update.message.reply_text(msghello)
    context.job_queue.run_once(scheduled_update, randomSleep(), context=chat_id, name=str(chat_id))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    
def add_url(update: Update, context: CallbackContext) -> None:
    #ADD URL
    text = update.message.text
    URLLIST.append(text)
    update.message.reply_text(text="Url has been Added")

def testdelete(update: Update, context: CallbackContext) -> None:
    anuncioid_db.popitem()
    return
def listurl(update: Update, context: CallbackContext) -> None:
    for u in URLLIST:
        update.message.reply_text(u)
    return

def msgnormal(update: Update, context: CallbackContext) -> None:
    add_url(update,context)
    listurl(update,context)
    
#------------------------/TELEGRAM--------------------------------
def main():
    #"Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    #Aqui se definen los  comandos y las funciones asociadas
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("url", add_url))
    dispatcher.add_handler(CommandHandler("listurl", changefreq))
    dispatcher.add_handler(CommandHandler("testdelete", testdelete))
   
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, msgnormal))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    #updateList(url)
    
    print('idle end')
    
    
if __name__ == '__main__':
    helpdesc="1-Create a telegram bot with @botfather.\n"\
                "2-Get the TOKEN and save it to a file\n"\
                    "3-Run this and give him URLs\n"
    
    parser = argparse.ArgumentParser(description=helpdesc)
    parser.add_argument('-t', '--token', required=False, help='TOKEN from @botfather', type=str)
    parser.add_argument('-tf', '--tokenfile', required=False, help='FILE .txt where the token is', type=str)
    parser.add_argument('-uf', '--urlfile', required=False, help='FILE .txt with the list of search urls', type=str)
    parser.add_argument('-u', '--url', required=False, help='Single search url', type=str)
    parser.add_argument('-mins', '--minsleep', required=True, help='Minimum amount of seconds between requests', type=str)
    parser.add_argument('-maxs', '--maxsleep', required=True, help='Maximum amount of seconds between requests', type=str)
    
    args = parser.parse_args()
    
    if (args.token==None)&(args.tokenfile==None):
        print("Failure to start token")
    
    TOKEN=args.token
    if (args.tokenfile!=None):
        with open(args.tokenfile) as f:
            TOKEN = f.readline()
            
    #LOADING URLS
    if(TOKEN!=None):
        print('Starting bot: '+TOKEN)
        if args.urlfile!=None:
            with open(args.urlfile) as f:
                URLLIST=f.readlines()
        if args.url!=None:
            URLLIST.append(args.url)
        
        print('Loaded URLS:')
        for item in URLLIST:
            print(item)
    MINS=int(args.minsleep)
    MAXS=int(args.maxsleep)
    
    main()
