import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_conversa_mensagem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='conversa',
            name='criador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversas_criadas', to=settings.AUTH_USER_MODEL, verbose_name='Criado por'),
        ),
        migrations.AddField(
            model_name='mensagem',
            name='anexo',
            field=models.FileField(blank=True, upload_to='conversas/%Y/%m/', verbose_name='Anexo'),
        ),
        migrations.AddField(
            model_name='mensagem',
            name='anexo_mime',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='mensagem',
            name='anexo_nome',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='mensagem',
            name='anexo_tipo',
            field=models.CharField(blank=True, choices=[('audio', 'Áudio'), ('imagem', 'Imagem'), ('arquivo', 'Arquivo')], max_length=10),
        ),
        migrations.AlterField(
            model_name='mensagem',
            name='texto',
            field=models.TextField(blank=True, max_length=1000, verbose_name='Mensagem'),
        ),
    ]
