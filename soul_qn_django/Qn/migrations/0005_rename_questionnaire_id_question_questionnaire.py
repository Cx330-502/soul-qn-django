# Generated by Django 4.1 on 2023-05-16 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Qn", "0004_rename_questionnaire_question_questionnaire_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="question",
            old_name="questionnaire_id",
            new_name="questionnaire",
        ),
    ]
