from django.core.management.base import BaseCommand

from gemet.thesaurus.exports import create_export_files


class Command(BaseCommand):
    help = 'Create initial export files'

    def handle(self, *args, **options):
        create_export_files()
