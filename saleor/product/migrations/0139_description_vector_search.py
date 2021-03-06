# Generated by Django 3.1.5 on 2021-01-14 08:31

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


def parse_description_json_to_string(description):
    string = ""
    blocks = description.get("blocks")
    if not blocks or not isinstance(blocks, list):
        return ""
    for block in blocks:
        block_type = block["type"]
        if block_type == "list":
            for item in block["data"].get("items"):
                if not item:
                    continue
                string += item
        else:
            text = block["data"].get("text")
            if not text:
                continue
            string += text
    return string


def migrate_description_into_description_plaintext(apps, schema):
    Product = apps.get_model("product", "Product")
    for product in Product.objects.iterator():
        product.description_plaintext = parse_description_json_to_string(
            product.description
        )
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0138_migrate_description_json_into_description"),
    ]
    replaces = [
        ("product", "0130_create_product_description_search_vector"),
        ("product", "0131_update_ts_vector_existing_product_name"),
    ]
    operations = [
        migrations.AddField(
            model_name="product",
            name="description_plaintext",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="product",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="product_pro_search__e78047_gin"
            ),
        ),
        migrations.RunSQL(
            """
            CREATE TRIGGER title_vector_update BEFORE INSERT OR UPDATE
            ON product_product FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(
                'search_vector', 'pg_catalog.english', 'description_plaintext'
            );
        """
        ),
        migrations.RunPython(
            migrate_description_into_description_plaintext,
            migrations.RunPython.noop,
        ),
    ]
