# -*- coding: utf-8 -*-
from django.db import migrations, models
import exact.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_url', models.URLField(help_text='E.g https://start.exactonline.nl/api', verbose_name='API base URL')),
                ('client_id', models.CharField(help_text='Your OAuth2/Exact App client ID', max_length=255)),
                ('client_secret', models.CharField(help_text='Your OAuth2/Exact App client secret', max_length=255)),
                ('redirect_uri', models.URLField(help_text='Callback URL on your server. https://example.com/exact/authenticate', verbose_name='OAuth2 redirect URI')),
                ('division', models.IntegerField()),
                ('access_expiry', models.IntegerField(blank=True, null=True)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('authorization_code', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(choices=[('Accounts', 'Accounts'), ('BankAccounts', 'Bank Accounts'), ('Contacts', 'Contacts'), ('CostTransactions', 'CostTransactions'), ('DocumentAttachments', 'Document Attachments'), ('Documents', 'Documents'), ('FinancialTransactions', 'FinancialTransactions'), ('GoodsDeliveries', 'GoodsDeliveries'), ('Items', 'Items'), ('ProjectPlanning', 'ProjectPlanning'), ('PurchaseOrders', 'PurchaseOrders'), ('Quotations', 'Quotations'), ('SalesInvoices', 'SalesInvoices'), ('SalesOrders', 'SalesOrders'), ('StockPositions', 'StockPositions'), ('TimeTransactions', 'TimeTransactions')], max_length=255, unique=True)),
                ('callback', models.URLField(default=exact.models._default_callback_url, help_text='Webhook callback', verbose_name='Callback')),
                ('guid', models.CharField(blank=True, max_length=36, null=True)),
            ],
        ),
    ]
