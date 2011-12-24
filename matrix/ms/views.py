# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
import re
import random
import logging
import httplib
from matrix.settings import AWS_MS_PHOTOS, SMSing
from matrix.ms.models import Game, Player

from util import send_death_announcement, send_thxfeedback, send_win_annoucement, shuffle_for_game, prune_game, send_game_welcome, send_game_feedback_request, render_inactive


logger = logging.getLogger(__name__)


def get_active_game(request):
    games = Game.objects.filter(is_done=False, is_closed=False).order_by('-id')
    if not games:
        return HttpResponse('X')
    else:
        return HttpResponse(games[0].id)
        
def register(request, game_id, photo_file):
    """ register a player for a game, validate the cell out of the photo and pass back number of registered game players or err msg 
        if there is an error
    """
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")

    if not game.is_closed:
        try:
            cell, photo_url = validate_registration(photo_file)
            p = Player.objects.get(game=game, cell=cell)
        except Player.DoesNotExist:
            p = Player(game=game, photo_url=photo_url, cell=cell)
            p.save()
            p.initialize()
        except MSException, e:
            logger.info("Didn't validate something!", exc_info=True)
            return HttpResponse("Upload failed. Check phone # and try again.")
        return HttpResponse (game.active_count())
    else:
        return HttpResponse("Game is closed")


def admin_start(request):
    """ return list of games to start one """
    games = Game.objects.filter(is_done=False, is_closed=False)
    return render_to_response('ms/admin_start.html', RequestContext(request, {'games': games}))
    
    
def start_game(request, game_id):
    """ closes the game, shuffles the players and starts it. We return # of active players """
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    if SMSing:
        game.is_closed = True
    game.save()
    logger.debug("Going to shuffle for game %s" % game)
    shuffle_for_game(game)
    logger.debug("Done shuffling for game %s. Going to send welcome SMSes." % game)
    if SMSing:
        send_game_welcome(game)
    activePlayers = game.active_count()
    logger.debug("Sent to %i players for game %s." % ( activePlayers, game))
    return HttpResponseRedirect('/m/status/%s' % game.id)
    
    
    
def go(request, permalink):
    """ howto, presumed to be first load of applicaiton """
    try:
        player = Player.objects.get(permalink=permalink)
    except Player.DoesNotExist, pe:
        logger.debug ("Permalink %s doesn't tie on first load to an existing player" % permalink)
        return render_to_response('ms/error.html' , RequestContext(request))
    if player.is_active and not player.has_died:
        # we mark him as started:
        player.has_started = True
        player.save()
        return render_to_response('ms/howto.html', RequestContext(request, {'player': player}))
    else:
        return render_to_response('ms/howto.html', RequestContext(request,{'player': player}))

def play(request, permalink):
    """ this is a unique key that starts a player playing. Pass back all the relevant bits in 
        a mobile template. Is idempotent unless the player is_active is false or the player has been killed
    """
    try:
        player = Player.objects.get(permalink=permalink)
    except Player.DoesNotExist, pe:
        logger.debug ("Permalink %s doesn't tie to an existing player" % permalink)
        return render_to_response('ms/error.html' , RequestContext(request))
    if player.is_active and not player.has_died:
        return render_to_response('ms/play.html', RequestContext(request, {'player': player}))
    else:
        return render_to_response('ms/error.html' , RequestContext(request, {'player': player}))

@csrf_exempt
def attempt_kill(request, permalink):
    """ check for whether this player has killed the other. Param killcode is in form If so, pass new info; if not pass FAIL """
    try:
        player = Player.objects.get(permalink=permalink)
    except Player.DoesNotExist, pe:
        logger.info("In an attempted kill, player permalink: %s not recognized" % permalink)
        return render_to_response('ms/error.html' , RequestContext(request))
    kill_code = request.POST.get('killcode','')
    if player.target.kill_code == kill_code.strip():
        try:
            old_target = player.killed_target()
            notify_of_death(old_target)
            if old_target.target == player:
                # this is a win case!
                notify_of_win(player)
                return render_to_response('ms/win.html' , RequestContext(request, {'player': player}))
            else:
                return render_to_response('ms/yeskill.html' , RequestContext(request, {'player': player}))
        except:
            logger.warn("Ran into trouble execing kill for playerid %i" % player.id, exc_info=True)
    else:
        return render_to_response('ms/nokill.html' , RequestContext(request, {'player': player}))

@csrf_exempt
def take_feedback(request):
    """ the endpoint that Twilio wil call when people reply """
    from_num = request.POST.get("From", "")
    feedback = request.POST.get("Body", "")
    logger.debug("Feedback from %s: '%s'" % (from_num, feedback))
    numkey = from_num[2:]
    try:
        possiblePlayers = Player.objects.filter(cell=numkey)
        for p in possiblePlayers:
            p.feedback = p.feedback + ' ' + feedback
            p.save()
            send_thxfeedback(p)
    except:
        logger.error("Problem getting feedback from %s '%s'" % (from_num, feedback), exc_info=True)
    return HttpResponse("")

def feedback_report(request, game_id):
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    return render_to_response('ms/feedback_summary.html' , RequestContext(request, {'g': game}))
    
def send_feedback_request(request, game_id):
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    send_game_feedback_request(game)
    return HttpResponse("Feedback request sent!")
    
def status(request, game_id):
    """ return status which is total_players, total_started, total_alive """
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    return render_to_response('ms/status.html' , RequestContext(request, {'g': game}))

def list_actives(request, game_id):
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    
    activePlayers = list(game.player_set.filter(is_active=True, has_died=False))
    activePlayers.sort(key=lambda x:x.cell)
    return render_to_response('ms/actives.html' , RequestContext(request, {'actives': activePlayers}))

def prune_inactives(request, game_id):
    """ take anyone who hasn't started and cut them out of the game by rewiring folks"""
    try: 
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return HttpResponse("Game can't be found")
    prune_game(game)
    return HttpResponseRedirect('/m/status/%s' % game.id)
    
def player_status(request, permalink):
    try:
        player = Player.objects.get(permalink=permalink)
    except Player.DoesNotExist, pe:
        logger.debug ("Permalink %s doesn't tie on first load to an existing player" % permalink)
        return render_to_response('ms/error.html' , RequestContext(request))
    return render_to_response('ms/playerstatus.html' , RequestContext(request, {'p': player}))
        
    
def make_inactive(request, permalink):
    """ takes a particular player out of the game """
    try:
        player = Player.objects.get(permalink=permalink)
    except Player.DoesNotExist, pe:
        logger.debug ("Permalink %s doesn't tie on first load to an existing player" % permalink)
        return render_to_response('ms/error.html' , RequestContext(request))
    render_inactive(player)
    return HttpResponseRedirect('/m/actives/%s' % player.game.id)
        
    


def prize(request):
    """ prize info """
    return render_to_response('ms/prize.html', RequestContext(request))

# utility functions below

def notify_of_death(dead_guy):
    """ send notification that dead_guy is out """
    if SMSing:
        send_death_announcement(dead_guy)

def notify_of_win(winner):
    if SMSing:
        send_win_annoucement(winner)
    
def test_exists(photo_name):
    """ head AWS for a file """
    try:
        con = httplib.HTTPConnection(AWS_MS_PHOTOS)
        print 'url is %s and name is %s' % (AWS_MS_PHOTOS, photo_name)
        con.request('HEAD', '/%s' % photo_name)
        res = con.getresponse()
        size = int(res.getheader('content-length'))
        print 'size back %s' % size
        if size > 0: 
            return True
        else:
            return False
    except:
        logging.error("Had a bad fall validating photo %s" % photo_name, exc_info=True)
        return False
        

    
class MSException(Exception): pass

def validate_registration(photo_file):
    """ returns the parsed phone # and the photo_url to store """
    try:
        print photo_file
        phone, rest = photo_file.split('.')
        photo_url = 'http://%s/%s' % (AWS_MS_PHOTOS, photo_file)
        if test_exists(photo_file):
            return (phone, photo_url)
        else:
            logger.error("This file doesn't compute on AZ: %s" % photo_file)
            raise MSException("Could not find photo existing") 
    except Exception, ex:
        m = 'failed dramatically on parsing valid phone #'
        print m
        logger.error("Going to reject this request", exc_info=True)
        raise (MSException(m))
    
    