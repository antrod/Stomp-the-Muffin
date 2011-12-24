# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Player.sms_sent'
        db.add_column('ms_player', 'sms_sent', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Player.feedback'
        db.add_column('ms_player', 'feedback', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Player.sms_sent'
        db.delete_column('ms_player', 'sms_sent')

        # Deleting field 'Player.feedback'
        db.delete_column('ms_player', 'feedback')


    models = {
        'ms.game': {
            'Meta': {'object_name': 'Game'},
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'ms.player': {
            'Meta': {'object_name': 'Player'},
            'cell': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'feedback': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ms.Game']"}),
            'has_died': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'kill_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'kill_phrase': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'killed_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['ms.Player']"}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'photo_url': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sms_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['ms.Player']"})
        }
    }

    complete_apps = ['ms']
