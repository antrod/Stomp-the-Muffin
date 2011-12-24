# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Player.target'
        db.alter_column('ms_player', 'target_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['ms.Player']))

        # Changing field 'Player.killed_by'
        db.alter_column('ms_player', 'killed_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['ms.Player']))


    def backwards(self, orm):
        
        # Changing field 'Player.target'
        db.alter_column('ms_player', 'target_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ms.Player']))

        # Changing field 'Player.killed_by'
        db.alter_column('ms_player', 'killed_by_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ms.Player']))


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
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ms.Game']"}),
            'has_died': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'kill_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'kill_phrase': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'killed_by': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'related_name': "'+'", 'null': 'True', 'to': "orm['ms.Player']"}),
            'last_access': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'photo_url': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'related_name': "'+'", 'null': 'True', 'to': "orm['ms.Player']"})
        }
    }

    complete_apps = ['ms']
