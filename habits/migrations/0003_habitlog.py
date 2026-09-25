from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HabitLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('completed', models.BooleanField(default=True, verbose_name='Выполнена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('habit', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='logs',
                    to='habits.habit',
                    verbose_name='Привычка',
                )),
            ],
            options={
                'verbose_name': 'Выполнение',
                'verbose_name_plural': 'Выполнения',
                'ordering': ['-date'],
                'unique_together': {('habit', 'date')},
            },
        ),
    ]
