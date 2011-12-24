#!/usr/bin/python


import os, sys, random, time

import traceback

from matrix.ms.models import KillPhrase, Game, Player
from matrix.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUM, SMSing
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
import logging

logger = logging.getLogger(__name__)

try:
    adminPlayer = Player.objects.filter(cell='cell-of-the-admin')[0]
except IndexError:
    # first load!
    # g = Game(name="Xmas Party")
    # g.save()
    # p = Player(cell='cell-of-the-admin', game=g, photo_url='http://ms.matrix.vc/cell-of-the-admin.jpg')
    #p.save()
    # adminPlayer = p
    adminPlayer = None

def send_sms(player, msg):
    """ sends a message, returns True if Twilio takes it which may not mean anything other than the # is properly formatted
        very cheap as we don't store the sid or check for anything other than errors
    """
    if SMSing:
        try:
            client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.sms.messages.create(to='+1'+ player.cell , from_=TWILIO_FROM_NUM, body=msg)
            return True
        except TwilioRestException:
            return False
    else:
        logger.info("Not sending this message '%s' to %s" % (msg, player))

def send_thxfeedback(player):
    msg = "Thanks for the feedback. We promise not to text you again until the next Stomp!"
    send_sms(player, msg)

def send_reassignment(player):
    msg = "Your target muffin has gone stale (or they left), check out your new target here: http://matrix.vc/m/go/%s" % player.permalink
    send_sms(player, msg)

def send_deactivate(player):
    msg = "Looks like you might have left (or have an old phone). You are no longer playing but better luck next year."
    send_sms(player, msg)
    
def send_death_announcement(player):
    msg = "It looks like you've been stomped! Thanks for playing."
    send_sms(player, msg)

def send_win_annoucement(player):
    msg = "You've won! Congratulations!"
    send_sms(player, msg)
    adminPlayer = Player.objects.filter(cell='cell-of-the-admin')[0]
    send_sms(adminPlayer, "%s won. His picture: http://ms.matrix.vc/%s.jpg" % (player.cell, player.cell))
    
    
def send_game_welcome(game):
    msg = "Ready to play the Matrix holiday game? Click here http://matrix.vc/m/go/%s to start & learn how. Happy stomping!"
    
    for p in game.player_set.filter(is_active=True, has_died=False):
        if not p.sms_sent:
            tries = 3
            while tries:
                if send_sms(p, msg % p.permalink):
                    p.sms_sent = True
                    p.save()
                    break
                else:
                    print 'tried to send to %s for the %i time and failed' % ( p.cell, tries)
                    tries = tries - 1 
                    time.sleep (0.5)
                if tries == 0:
                    p.is_active = False
                    p.save()

def send_game_feedback_request(game):
    msg = "Thanks for playing. Please rate us 1-5 with 5 being the most fun you've had this year. Reply to this message with the # & any comments."
    for p in game.player_set.filter(has_started=True):
        send_sms(p, msg)


def shuffle_for_game(game):
    players = list(game.player_set.all())
    phrases = list(game.killphrase_set.all())
    random.shuffle(players)
    random.shuffle(phrases)
    for i, p in enumerate(players):
        if i < len(players)-1:
            p.target = players[i+1]
        else:
            p.target = players[0]
        p.kill_phrase = phrases.pop().phrase
        p.has_started = False
        p.is_active   = True
        p.sms_sent    = False
        p.has_died    = False
        p.killed_by   = None
        p.save()
        

def render_inactive(player):
    """ render a player inactive and close the chain """
    logger.debug("player %s has target %s" % (player, player.target))
    try:
        previous_player = player.game.player_set.filter(target=player)[0]
        logger.debug("And player %s has player %s as his target" % (previous_player, player))
    except:
        logger.error("Cant prune %s" % player, exc_info=True)
        return
    if player.target:
        previous_player.target = player.target
        previous_player.save()
        send_reassignment(previous_player)
    
    player.has_died = True
    player.is_active = False
    player.target = None
    player.save()
    
    if player.game.player_set.filter(has_died=False).count() == 1:
        send_win_annoucement(player)
    else:
        send_deactivate(player)
        


def prune_game(game):
    """ shrink a game and close the chain """
    deadbeats = game.player_set.filter(has_started=False)
    for p in deadbeats:
        render_inactive(p)

    
     
# these are for prefilling the database with stuff:
        
def generate_players(game_id, num=25):
    for i in range(num):
        cell = '%010d' % i
        p = Player(game_id=game_id, photo_url='http://ms.matrix.vc/cell-of-the-admin.jpg', cell=cell)
        p.save()
        p.initialize()
    
    
def generate_phrasefile(game_id, num):
    fout = open('%s.txt' % game_id, 'w')
    for i in range(num):
        try:
            l = os.popen('fortune -a -n 100').read()
            if len(l) > 50 and len(l):
                fout.write(l[0:50])
        except:
            print 'missed %s' % l
    fout.close()
    
def populate_phrases(game_id):
    """ look for the game id txt file in this dir """
    for line in file('%s.txt' % game_id):
        try:
            garbage =line.strip()
            phrase = KillPhrase(game_id=game_id, phrase=garbage)
            phrase.save()
        except Exception, ex:
            traceback.print_exc()


if __name__== '__main__':
    # generate_phrasefile(sys.argv[1], 200)
    populate_phrases(sys.argv[1])
    # generate_players(1)
    #send_game_welcome(Game.objects.get(pk=1))
    