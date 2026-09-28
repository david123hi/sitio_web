from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TipoCocina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'verbose_name': 'Tipo de cocina',
                'verbose_name_plural': 'Tipos de cocina',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Restaurante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('nombre', models.CharField(max_length=150)),
                ('ciudad', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('rango_precio', models.CharField(choices=[('$', 'Económico ($)'), ('$$', 'Moderado ($$)'), ('$$$', 'Premium ($$$)')], default='$$', max_length=3)),
                ('calificacion', models.DecimalField(decimal_places=1, max_digits=2)),
                ('descripcion', models.TextField()),
                ('imagen', models.CharField(blank=True, max_length=200)),
                ('tipo_cocina', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='restaurantes', to='restaurantes.tipococina')),
            ],
            options={
                'verbose_name': 'Restaurante',
                'verbose_name_plural': 'Restaurantes',
                'ordering': ['nombre'],
            },
        ),
    ]
