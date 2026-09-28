from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Continente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Continente',
                'verbose_name_plural': 'Continentes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Destino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('nombre', models.CharField(max_length=150)),
                ('pais', models.CharField(max_length=100)),
                ('precio_clp', models.PositiveIntegerField()),
                ('duracion_dias', models.PositiveIntegerField()),
                ('descripcion', models.TextField()),
                ('imagen', models.CharField(blank=True, max_length=200)),
                ('continente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='destinos', to='destinos.continente')),
            ],
            options={
                'verbose_name': 'Destino',
                'verbose_name_plural': 'Destinos',
                'ordering': ['nombre'],
            },
        ),
    ]
