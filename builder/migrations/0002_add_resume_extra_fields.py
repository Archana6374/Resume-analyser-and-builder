from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='github',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='resume',
            name='portfolio',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='resume',
            name='activities',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='resume',
            name='certifications',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='resume',
            name='projects',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='resume',
            name='template',
            field=models.CharField(blank=True, default='classic', max_length=50),
        ),
    ]
