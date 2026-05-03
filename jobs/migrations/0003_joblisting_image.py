from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_joblisting_latitude_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='jobs/'),
        ),
    ]
