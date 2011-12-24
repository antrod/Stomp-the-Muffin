#!/usr/bin/python

import sys
from matrix.ms.models import Game

def reset(game_id):
    try:
        g = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        print 'game doesnt exist'
        sys.exit(0)
    
    g.is_done = False
    g.is_closed = False
    g.save()

    for p in g.player_set.all():
        p.delete()
    return 'Just reset game %s' % game_id


if __name__ == '__main__':
    reset(1)
    