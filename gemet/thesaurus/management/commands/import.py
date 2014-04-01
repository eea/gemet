from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Import a set of terms into the database'

    def handle(self, *args, **options):
        raise CommandError('Not implemented')
