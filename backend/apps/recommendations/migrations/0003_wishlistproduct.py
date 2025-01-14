# Generated by Django 4.2.8 on 2024-11-26 02:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recommendations', '0002_remove_recommendationresult_explanation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishlistProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(choices=[('deposit', '예금'), ('saving', '적금')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deposit_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.depositproduct')),
                ('saving_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.savingproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'deposit_product'), ('user', 'saving_product')},
            },
        ),
    ]
