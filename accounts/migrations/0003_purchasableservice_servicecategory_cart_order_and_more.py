# Generated by Django 5.0.7 on 2025-07-04 04:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_hostingplan_alter_user_options_user_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchasableService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre del Servicio')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('short_description', models.CharField(max_length=255, verbose_name='Descripción Corta')),
                ('price_monthly', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Mensual')),
                ('price_quarterly', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Trimestral')),
                ('price_semiannual', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Semestral')),
                ('price_annual', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Anual')),
                ('price_biennial', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Bienal')),
                ('price_one_time', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio Único')),
                ('features', models.JSONField(default=list, help_text='Lista de características del servicio', verbose_name='Características')),
                ('specifications', models.JSONField(default=dict, help_text='Especificaciones técnicas', verbose_name='Especificaciones')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Destacado')),
                ('requires_domain', models.BooleanField(default=False, verbose_name='Requiere Dominio')),
                ('setup_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Costo de Configuración')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
            ],
            options={
                'verbose_name': 'Servicio Comprable',
                'verbose_name_plural': 'Servicios Comprables',
                'ordering': ['-is_featured', 'category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('icon', models.CharField(default='fas fa-cog', max_length=50, verbose_name='Icono FontAwesome')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('order', models.IntegerField(default=0, verbose_name='Orden')),
            ],
            options={
                'verbose_name': 'Categoría de Servicio',
                'verbose_name_plural': 'Categorías de Servicios',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Carrito',
                'verbose_name_plural': 'Carritos',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=20, unique=True, verbose_name='Número de Orden')),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('processing', 'Procesando'), ('completed', 'Completada'), ('cancelled', 'Cancelada'), ('failed', 'Fallida')], default='pending', max_length=20, verbose_name='Estado')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Subtotal')),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Impuestos')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total')),
                ('billing_name', models.CharField(max_length=200, verbose_name='Nombre de Facturación')),
                ('billing_email', models.EmailField(max_length=254, verbose_name='Email de Facturación')),
                ('billing_address', models.TextField(verbose_name='Dirección de Facturación')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Órdenes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=200, verbose_name='Nombre del Servicio')),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Mensual'), ('quarterly', 'Trimestral'), ('semiannual', 'Semestral'), ('annual', 'Anual'), ('biennial', 'Bienal'), ('one_time', 'Pago Único')], max_length=20, verbose_name='Ciclo de Facturación')),
                ('quantity', models.PositiveIntegerField(verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Unitario')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Total')),
                ('domain_name', models.CharField(blank=True, max_length=255, verbose_name='Nombre de Dominio')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='accounts.order', verbose_name='Orden')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.purchasableservice', verbose_name='Servicio')),
            ],
            options={
                'verbose_name': 'Item de Orden',
                'verbose_name_plural': 'Items de Orden',
            },
        ),
        migrations.AddField(
            model_name='purchasableservice',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.servicecategory', verbose_name='Categoría'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Mensual'), ('quarterly', 'Trimestral'), ('semiannual', 'Semestral'), ('annual', 'Anual'), ('biennial', 'Bienal'), ('one_time', 'Pago Único')], max_length=20, verbose_name='Ciclo de Facturación')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('domain_name', models.CharField(blank=True, max_length=255, verbose_name='Nombre de Dominio')),
                ('notes', models.TextField(blank=True, verbose_name='Notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='accounts.cart', verbose_name='Carrito')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.purchasableservice', verbose_name='Servicio')),
            ],
            options={
                'verbose_name': 'Item del Carrito',
                'verbose_name_plural': 'Items del Carrito',
                'unique_together': {('cart', 'service', 'billing_cycle')},
            },
        ),
    ]
