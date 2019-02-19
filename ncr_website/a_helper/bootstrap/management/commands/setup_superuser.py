from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not User.objects.filter(
                username=settings.SUPERUSER_USER).exists():

            id = User.objects.create(is_superuser=True,
                                     is_staff=True,
                                     username=settings.SUPERUSER_USER,
                                     email=settings.SUPERUSER_EMAIL,
                                     password="!",
                                     first_name="Admin",
                                     last_name="User")

            # Manually set the password to something
            # simple for these environments
            id.set_password(settings.SUPERUSER_PASSWORD)
            id.save()
