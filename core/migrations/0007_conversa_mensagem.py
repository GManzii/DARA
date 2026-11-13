import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_empresa_codigo_convite_funcionario'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('pedro', 'Pedro (assistente)'), ('grupo', 'Grupo da empresa')], max_length=10, verbose_name='Tipo')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome')),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conversas', to='core.empresa', verbose_name='Empresa')),
                ('participantes', models.ManyToManyField(related_name='conversas', to=settings.AUTH_USER_MODEL, verbose_name='Participantes')),
            ],
            options={
                'verbose_name': 'Conversa',
                'verbose_name_plural': 'Conversas',
            },
        ),
        migrations.CreateModel(
            name='Mensagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(max_length=1000, verbose_name='Mensagem')),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mensagens_enviadas', to=settings.AUTH_USER_MODEL)),
                ('conversa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='core.conversa')),
            ],
            options={
                'verbose_name': 'Mensagem',
                'verbose_name_plural': 'Mensagens',
                'ordering': ['criada_em', 'id'],
            },
        ),
    ]
