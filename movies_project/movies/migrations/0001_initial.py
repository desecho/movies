# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'movies_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('preferences', self.gf('annoying.fields.JSONField')(default='{"lang": "ru"}')),
        ))
        db.send_create_signal(u'movies', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'movies_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'movies.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'movies_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'movies.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'List'
        db.create_table(u'movies_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'movies', ['List'])

        # Adding model 'Movie'
        db.create_table(u'movies_movie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('title_ru', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('overview', self.gf('django.db.models.fields.TextField')(null=True)),
            ('plot', self.gf('django.db.models.fields.TextField')(null=True)),
            ('director', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('writer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('actors', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('imdb_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15)),
            ('tmdb_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('imdb_rating', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=2, decimal_places=1)),
            ('poster_ru', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('poster_en', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('release_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('runtime', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('homepage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('trailers', self.gf('annoying.fields.JSONField')(null=True)),
        ))
        db.send_create_signal(u'movies', ['Movie'])

        # Adding model 'Record'
        db.create_table(u'movies_record', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.User'])),
            ('movie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.Movie'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.List'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'movies', ['Record'])

        # Adding model 'Action'
        db.create_table(u'movies_action', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'movies', ['Action'])

        # Adding model 'ActionRecord'
        db.create_table(u'movies_actionrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.User'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.Action'])),
            ('movie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.Movie'])),
            ('list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.List'], null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'movies', ['ActionRecord'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'movies_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'movies_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'movies_user_user_permissions'))

        # Deleting model 'List'
        db.delete_table(u'movies_list')

        # Deleting model 'Movie'
        db.delete_table(u'movies_movie')

        # Deleting model 'Record'
        db.delete_table(u'movies_record')

        # Deleting model 'Action'
        db.delete_table(u'movies_action')

        # Deleting model 'ActionRecord'
        db.delete_table(u'movies_actionrecord')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'movies.action': {
            'Meta': {'object_name': 'Action'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'movies.actionrecord': {
            'Meta': {'object_name': 'ActionRecord'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.Action']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.List']", 'null': 'True', 'blank': 'True'}),
            'movie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.Movie']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.User']"})
        },
        u'movies.list': {
            'Meta': {'object_name': 'List'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'movies.movie': {
            'Meta': {'ordering': "['pk']", 'object_name': 'Movie'},
            'actors': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'director': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'imdb_rating': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '1'}),
            'overview': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'plot': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'poster_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'poster_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'runtime': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tmdb_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'trailers': ('annoying.fields.JSONField', [], {'null': 'True'}),
            'writer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        u'movies.record': {
            'Meta': {'object_name': 'Record'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.List']"}),
            'movie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.Movie']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['movies.User']"})
        },
        u'movies.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'preferences': ('annoying.fields.JSONField', [], {'default': '\'{"lang": "ru"}\''}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['movies']