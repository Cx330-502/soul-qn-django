# Generated by Django 4.1 on 2023-05-16 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Qn", "0003_rename_questionnaire_id_question_questionnaire"),
    ]

    operations = [
        migrations.RenameField(
            model_name="question",
            old_name="questionnaire",
            new_name="questionnaire_id",
        ),
    ]
