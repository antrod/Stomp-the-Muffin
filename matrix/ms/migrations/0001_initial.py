# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Game'
        db.create_table('ms_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('ms', ['Game'])

        # Adding model 'Player'
        db.create_table('ms_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ms.Game'])),
            ('photo_url', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('cell', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('permalink', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('last_access', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('has_started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_died', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('kill_phrase', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('kill_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('killed_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ms.Player'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['ms.Player'])),
        ))
        db.send_create_signal('ms', ['Player'])


    def backwards(self, orm):
        
        # Deleting model 'Game'
        db.delete_table('ms_game')

        # Deleting model 'Player'
        db.delete_table('ms_player')


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
            'killed_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ms.Player']"}),
            'last_access': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'permalink': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'photo_url': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['ms.Player']"})
        }
    }

    complete_apps = ['ms']
