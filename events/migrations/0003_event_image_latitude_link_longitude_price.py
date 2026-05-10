from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0002_eventrsvp_remove_event_rsvp_count'),
    ]
    operations = [
        migrations.AddField(model_name='event', name='image',     field=models.ImageField(blank=True, null=True, upload_to='events/')),
        migrations.AddField(model_name='event', name='price',     field=models.CharField(blank=True, default='', max_length=50)),
        migrations.AddField(model_name='event', name='latitude',  field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name='event', name='longitude', field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name='event', name='link',      field=models.URLField(blank=True, default='')),
    ]
