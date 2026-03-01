from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0004_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='assessment_method',
            field=models.CharField(verbose_name='考核方式', max_length=50, blank=True),
        ),
    ]

