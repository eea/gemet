# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from gemet.thesaurus.models import Property, Language

CHARACTER_REPLACEMENTS = (
    (u'\u0163', u'\u021b'),  # ţ, ț
    (u'\u0162', u'\u021a'),  # Ţ, Ț
    (u'\u015f', u'\u0219'),  # ş, ș
    (u'\u015e', u'\u0218'),  # Ş, Ș
)


class Command(BaseCommand):

    help = 'Command that corrects the romanian entries from database'

    def handle(self, *args, **options):
        romanian_language = Language.objects.get(code='RO')
        properties = Property.objects.filter(language=romanian_language)
        count = 0
        for element in properties:
            for old_character, new_character in CHARACTER_REPLACEMENTS:
                if element.value.find(old_character) != -1:
                    element.value = element.value.replace(old_character,
                                                          new_character)
                    element.save()
                    count += 1
        print str(count) + " Property objects changed."
