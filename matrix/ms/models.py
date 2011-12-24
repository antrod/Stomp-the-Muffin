from django.db import models
from django.contrib.auth.models import User
import random
import uuid
# Create your models here.


class Game(models.Model):
    name = models.CharField(max_length=200)
    date_added   = models.DateField(auto_now_add=True)
    is_closed    = models.BooleanField(default=False)
    is_done      = models.BooleanField(default=False)
    
    def active_count(self):
        return self.player_set.filter(is_active=True).count()
    
    def started_count(self):
        return self.player_set.filter(has_started=True).count()

    def killed_count(self):
        return self.player_set.filter(has_died=True).count()
    
    def sms_count(self):
        return self.player_set.filter(sms_sent=True).count()

    def feedback(self):
        return self.player_set.exclude(feedback__exact='')
        
    def __str__(self):
        return self.name


class Player(models.Model):
    game         = models.ForeignKey(Game)
    photo_url    = models.CharField(max_length=50)
    cell         = models.CharField(max_length=100)
    permalink    = models.SlugField(max_length=50)
    last_access  = models.DateTimeField(auto_now=True)
    
    is_active    = models.BooleanField(default=True)
    has_started  = models.BooleanField(default=False)
    has_died     = models.BooleanField(default=False)
    sms_sent     = models.BooleanField(default=False)

    kill_phrase  = models.CharField(max_length=255, blank=True)
    kill_code    = models.CharField(max_length=10, blank=True)    

    killed_by    = models.ForeignKey('self', related_name='+', null=True)
    target       = models.ForeignKey('self', related_name='+', null=True)
    
    feedback     = models.CharField(max_length=255, default='')

    def initialize(self):
        self.kill_code = random.randrange(10,1000)
        self.permalink = uuid.uuid4().hex
        self.save()
    
    def killed_target(self):
        """ move the player stats and return the killed target """
        old_target = self.target
        new_target = old_target.target
        
        old_target.has_died=True
        old_target.killed_by = self
        
        self.target = new_target
        
        old_target.save()
        self.save()
        return old_target

    def __str__(self):
        return self.cell


class KillPhrase(models.Model):
    game   = models.ForeignKey(Game)
    phrase = models.CharField(max_length=255, unique=True)
 
    def __str__(self):
        return self.phrase
  

