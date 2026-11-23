import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # Haute Couture
        migrations.CreateModel(
            name="HCDTeam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("teamName", models.CharField(max_length=200, unique=True)),
                ("submitPerformances", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="HCDTeamLeader",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fullName", models.CharField(max_length=100)),
                (
                    "contactNumber",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Contact number must contain exactly 10 digits.",
                                regex=r"^[0-9]{10}$",
                            )
                        ],
                    ),
                ),
                ("gender", models.CharField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], max_length=10)),
                ("email", models.EmailField(max_length=254)),
                (
                    "postalCode",
                    models.CharField(
                        max_length=6,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Postal code must contain exactly 6 digits.",
                                regex=r"^[0-9]{6}$",
                            )
                        ],
                    ),
                ),
                ("cityName", models.CharField(max_length=100)),
                (
                    "team",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leader",
                        to="core.hcdteam",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HCDMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                (
                    "contactNumber",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Contact number must contain exactly 10 digits.",
                                regex=r"^[0-9]{10}$",
                            )
                        ],
                    ),
                ),
                ("gender", models.CharField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], max_length=10)),
                (
                    "postalCode",
                    models.CharField(
                        max_length=6,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Postal code must contain exactly 6 digits.",
                                regex=r"^[0-9]{6}$",
                            )
                        ],
                    ),
                ),
                ("cityName", models.CharField(max_length=100)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="core.hcdteam",
                    ),
                ),
            ],
        ),

        # -- States of Dress (SOD) --
        migrations.CreateModel(
            name='SOD_Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=255, unique=True)),
                ('prev_performance', models.URLField(blank=True, max_length=500, null=True)),
                ('lead_name', models.CharField(max_length=255)),
                ('lead_gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], max_length=1)),
                ('lead_email', models.EmailField(max_length=254, unique=True)),
                ('lead_phone', models.CharField(max_length=15)),
                ('lead_city', models.CharField(blank=True, max_length=255, null=True)),
                ('lead_postal_code', models.CharField(blank=True, max_length=6, null=True)),
            ],
            options={
                'verbose_name': 'States of Dress Team',
                'verbose_name_plural': 'States of Dress Teams',
            },
        ),
        migrations.CreateModel(
            name='SOD_Member_detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], max_length=1)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=6, null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.sod_team')),
            ],
            options={
                'verbose_name': 'States of Dress Member',
                'verbose_name_plural': 'States of Dress Members',
            },
        ),
    ]
