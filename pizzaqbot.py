# -*- coding: utf-8 -*-

import requests
import textwrap
import logging
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import sqlite3
import re
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ParseMode
from HTMLParser import HTMLParser
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

BASEURL='https://9gag.com/'
listaGag = []
openedPQBos = []
drinkingPeople = []

#Parser cutre picado para 9gag
def ng_get_webm (idnr):
     nok = True
     while nok:
          randomSection = random.randint (0,8)
          randomGag = random.randint (0,8)
          sections = ['funny', 'awesome', 'gif', 'nsfw', 'video', 'wtf', 'comic', 'satisfying', 'science']
          print sections[randomSection] 
          r = requests.get (BASEURL + sections[randomSection])
          print r
          sub = r.text[r.text.find('GAG.App.loadConfigs(')+20:]
          js =  json.loads(sub[:sub.find('}}}).lo')+3])
          ret = "Error!"
          title = json.dumps(js['data']['posts'][randomGag]['title'])
          try:
               ret = json.dumps(js['data']['posts'][randomGag]['images']['image460sv']['url'])
               nok = False
          except:
               ret = json.dumps(js['data']['posts'][randomGag]['images']['image460']['url'])
               nok = False
          
          if ("webm" in ret) or ((idnr,ret) in listaGag):
               nok = True
     listaGag.append(tuple([idnr, ret])) 
     return title, ret


def start (bot, update):
     bot.send_message(chat_id=update.message.chat_id, text="PizzaQbot al habla, version 0.1. Padre, dame piernas")

def getNineGag (bot, update):
     idnr = update.message.chat_id
     gag = ng_get_webm(idnr)
     h = HTMLParser()
     bot.send_message(chat_id=idnr, text=h.unescape(gag[0]))
     bot.send_message(chat_id=idnr, text=h.unescape(gag[1]))

     
def saveQuote (bot, update, args):
     idnr = update.message.chat_id
     if len(args) == 0:
          bot.send_message(chat_id=idnr, text="Error! tiene que poner \"/nuevafrase frase célebre\"")
     else: 
          print " ".join(args)
          quotes = sqlite3.connect("quotes.db")
          cursor = quotes.cursor()
          cursor.execute ('INSERT INTO quotes (quote, idnr) VALUES  ("' + ' '.join(args)  +  '", "' + str(idnr) + '");')
          print "insertando"
          quotes.commit()
          print "insertado"
          quotes.close()
          bot.send_message(chat_id=idnr, text="Frase guardada correctamente")

def getQuote (bot, update):
     print "getquote"
     h = HTMLParser()
     quotes = sqlite3.connect("quotes.db")
     idnr = update.message.chat_id
     cursor = quotes.cursor()
     cursor.execute ("SELECT quote FROM quotes WHERE idnr = "+ str(idnr) + ";")
     lista = cursor.fetchall()
     ran = random.randint (0, len(lista) - 1)
     bot.send_message(chat_id=idnr, text=cowsay(lista[ran][0].encode('utf-8')))
     quotes.close()


def cowsay(str, length=40):
    return build_bubble(str, length) + build_cow() 

def build_cow():
    return """
         \  ^__^
          \  (oo)\_____
             (__)\         )\/\\
                 ||----w |
                 ||       ||
    """

def build_bubble(str, length=40):
    bubble = []

    lines = normalize_text(str, length)

    bordersize = len(lines[0])

    bubble.append("  " + "-" * bordersize)

    for index, line in enumerate(lines):
        border = get_border(lines, index)

        bubble.append("%s %s %s" % (border[0], line, border[1]))

    bubble.append("  " + "-" * bordersize)

    return "\n".join(bubble)

def normalize_text(str, length):
    lines  = textwrap.wrap(str, length)
    maxlen = len(max(lines, key=len))
    return [ line.ljust(maxlen) for line in lines ]

def get_border(lines, index):
    if len(lines) < 2:
        return [ "<", ">" ]

    elif index == 0:
        return [ "/", "\\" ]

    elif index == len(lines) - 1:
        return [ "\\", "/" ]

    else:
        return [ "|", "|" ]


def newpqbo (bot, update):
     idnr = update.message.chat_id
     
     for i in openedPQBos:
          if i[0] == idnr:
               bot.send_message(chat_id=idnr, text="Una sesión de PizzaQbo está ya abierta en este chat")
               return 1
     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
     pqbos = sqlite3.connect("pqbos.db")
     cursor = pqbos.cursor()
     cursor.execute ('INSERT INTO pqbos (idnr, pqbo_date) VALUES  ("' + str(idnr) + '", "' + timestamp + '");')
     print "insertando nuevo PizzaQbo"
     pqbos.commit()
     print "insertado"
     pqbos.close()
     bot.send_message(chat_id=idnr, text="Sesión de PizzaQbo abierta correctamente")
     openedPQBos.append(tuple([idnr, timestamp]))
     pqbos.close()     




def closepqbo (bot, update):
     idnr = update.message.chat_id     
     print openedPQBos
     for i, date in openedPQBos:
           if i == idnr:
               openedPQBos.remove(tuple([i,date]))
               drinkingPeople = []
               bot.send_message (chat_id=idnr, text="Sesión de PizzaQbo cerrada correctamente")
               return 0
     bot.send_message (chat_id=idnr, text="Error, ninguna sesión de PizzaQbo abierta en este chat")


def addpeopletopqbo (bot, update, args):
     idnr = update.message.chat_id
     if len(args) < 1:
          bot.send_message (chat_id=idnr, text="Error en el comando. El uso correcto del comando es: /addpeopletopqbo <nombre1>, <nombre2>, ...")
          return 1
     if pqbosession (idnr):
          people = (' '.join(args)).split(",")
          pqbos = sqlite3.connect("pqbos.db")
          cursor = pqbos.cursor()
          for person in people:
               trimmed = person.strip()
               drinkingPeople.append(tuple([trimmed, idnr]))
               cursor.execute('INSERT OR IGNORE INTO people (name, idnr, balance) VALUES ("'+trimmed+'","'+str(idnr)+'",0);')          
          bot.send_message (chat_id=idnr, text="Personas añadidas correctamente al sistema y a la sesión")
          pqbos.commit()
          pqbos.close()
          return 0
     bot.send_message(chat_id=idnr, text="No existe ninguna sesión de PizzaQbo abierta. Usa /newpqbo") 

def getcurrentpqbolist (bot, update):
     idnr = update.message.chat_id
     if pqbosession (idnr):
          pqbos = sqlite3.connect("pqbos.db")
          cursor = pqbos.cursor()
          message = "Lista de PizzaQboers en la sesión:\n"
          for i in drinkingPeople:
               cursor.execute ("SELECT name, balance FROM people WHERE name = '"+ i[0] + "';")
               lista = cursor.fetchall()
               message = message + "%s - Saldo: %f"%(lista[0]) + "\n"
          bot.send_message(chat_id=idnr, text=message)
     else:
          bot.send_message(chat_id=idnr, text="No exise ninguna sesión de PizzaQbo abierta. Usa /newpqbo")

def gettotalpqbolist (bot, update):
     idnr = update.message.chat_id
     pqbos = sqlite3.connect("pqbos.db")
     cursor = pqbos.cursor()
     cursor.execute ("SELECT name, balance FROM people WHERE people.idnr = %s"%str(idnr))
     message = "Lista de PizzaQboers:\n"
     lista = cursor.fetchall()
     for i in lista:
          message = message + "%s - Saldo: %f"%(i) + "\n"
     bot.send_message (chat_id=idnr, text=message)

def paycoins (bot, update, args):
     idnr = update.message.chat_id
     if len(args) < 2:
          bot.send_message (chat_id=idnr, text="Error en el comando. Uso correcto: /paycoins <nombre pagador>, <numero Qbocoins>")
          return 1
     if pqbosession(idnr):
          params = (''.join(args)).split(",")
          buyer = params[0].strip()
          quantity = float(params[1].strip())
          names = []
          for i in drinkingPeople:
               if (i[1] == idnr and i[0] != buyer):
                    names.append(i[0])
          if len(names) < 2:
               bot.send_message (chat_id=idnr, text="No hay suficientes personas registradas en la sesión, utiliza /addpeopletopqbo <lista de personas separada por comas>")
          pqbos = sqlite3.connect("pqbos.db")
          cursor = pqbos.cursor()
          cursor.execute ("UPDATE people SET balance = balance + %f WHERE (name = '%s' AND idnr = '%s');"%(quantity,buyer,idnr))
          debt = quantity / len(names)
          for i in names:
               cursor.execute("UPDATE people SET balance = balance - %f WHERE (name = '%s' AND idnr = '%s');"%(debt,i,idnr))
          pqbos.commit()
          pqbos.close()
          bot.send_message (chat_id=idnr, text="%s ha puesto %f Qbocoins. Restados %f Qbocoins al resto"%(buyer,quantity,debt))
     else:
          bot.send_message(chat_id=idnr, text="No exise ninguna sesión de PizzaQbo abierta. Usa /newpqbo")

def infopqbo (bot, update):
     idnr = update.message.chat_id
     message = '''
Guía de uso Qbocoins:
---------------------
1 Qbocoin equivale a 6,5€
Precio de un cubo: 1 Qbocoin
Precio de una pizza: 2 Qbocoin
---------------------
Uso de PizzaQbot:
/newpqbo : Abre una nueva sesión de PizzaQbo
/addpeopletopqbo <persona1>, <persona2>,...
     Incluye personas en la sesión en curso
     de PizzaQbo
/paycoins <persona>, <cantidad>: Registro de
     un pago en QboCoins
/getcurrentpqbolist : Lista de las personas
     registradas en la presente sesión y sus
     saldos acumulados
/gettotalpqbolist : Lista completa de saldos
     en el sistema PizzaQbot (acumulados)
/closepqbo : Cierra la sesión de PizzaQbo
     hasta abrir otra y los cambios en los
     saldos se quedan guardados en el
     acumulativo.
          
'''
     bot.send_message (chat_id=idnr, text=message)


def directcoins (bot, update, args):
     return 1


def pqbosession (idnr):
     for i, date in openedPQBos:
          if i == idnr:
               return True
     return False

def main ():
     # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     updater = Updater(token='<bot token>')
     dispatcher = updater.dispatcher
     start_handler = CommandHandler ('start', start)
     ninegag_handler = CommandHandler ('9gag', getNineGag)
     saveQuote_handler = CommandHandler ('nuevafrase', saveQuote, pass_args=True)
     getQuote_handler = CommandHandler ('fraserandom', getQuote)
     newpqbo_handler = CommandHandler ('newpqbo', newpqbo)
     closepqbo_handler = CommandHandler ('closepqbo', closepqbo)
     addpeopletopqbo_handler = CommandHandler ('addpeopletopqbo', addpeopletopqbo, pass_args=True)
     getcurrentpqbolist_handler = CommandHandler ('getcurrentpqbolist', getcurrentpqbolist)
     gettotalpqbolist_handler = CommandHandler ('gettotalpqbolist', gettotalpqbolist)
     paycoins_handler = CommandHandler ('paycoins', paycoins, pass_args=True)
     infopqbo_handler = CommandHandler ('infopqbo', infopqbo)
     dispatcher.add_handler(start_handler)
     dispatcher.add_handler(ninegag_handler)
     dispatcher.add_handler(saveQuote_handler)
     dispatcher.add_handler(getQuote_handler)
     dispatcher.add_handler(newpqbo_handler)
     dispatcher.add_handler(closepqbo_handler)
     dispatcher.add_handler(addpeopletopqbo_handler)
     dispatcher.add_handler(getcurrentpqbolist_handler)
     dispatcher.add_handler(gettotalpqbolist_handler)
     dispatcher.add_handler(paycoins_handler)
     dispatcher.add_handler(infopqbo_handler)
     updater.start_polling()

if __name__ == '__main__':
     main()

