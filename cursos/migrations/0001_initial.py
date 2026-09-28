from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Área',
                'verbose_name_plural': 'Áreas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('instructor', models.CharField(max_length=100)),
                ('nivel', models.CharField(choices=[('basico', 'Básico'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado')], default='basico', max_length=15)),
                ('duracion_horas', models.PositiveIntegerField()),
                ('precio_clp', models.PositiveIntegerField(default=0)),
                ('descripcion', models.TextField()),
                ('imagen', models.CharField(blank=True, max_length=200)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cursos', to='cursos.area')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
                'ordering': ['titulo'],
            },
        ),
    ]
