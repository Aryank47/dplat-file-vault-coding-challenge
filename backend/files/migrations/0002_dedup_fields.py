from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='hash',
            field=models.CharField(max_length=64, db_index=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='file',
            name='duplicate_of',
            field=models.ForeignKey(null=True, blank=True, related_name='duplicates', to='files.file', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='file',
            name='uploaded_by',
            field=models.CharField(max_length=255, db_index=True, default='anonymous'),
        ),
        migrations.AlterField(
            model_name='file',
            name='original_filename',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='file_type',
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
