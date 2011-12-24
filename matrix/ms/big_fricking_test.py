#!/usr/bin/python


from matrix.ms.models import Game, Player

g = Game.objects.get(pk=1)
for i in range(200):
    p = Player(game=g, cell='6175759474', photo_url='http://ms.matrix.vc/6175759474.jpg')
    p.save()
    p.initialize()
    