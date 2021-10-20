from collections import defaultdict

import re
import requests

from django.core.management.base import BaseCommand
from gemet.thesaurus.models import Property, Language
from gemet.thesaurus import PENDING, PUBLISHED


class Command(BaseCommand):
    help = "Extracts all links from concept sources and tests the URL's"

    def handle(self, *args, **options):
        props = Property.objects.filter(
            name="source",
            status__in=[PENDING, PUBLISHED],
            language=Language.objects.get(code="en"),
        ).all()
        self.stdout.write("Parsing {} sources for links".format(len(props)))
        links = defaultdict(list)
        for p in props:
            matches = re.findall(r"(?P<url>https?://[^\s]+)", p.value)
            for url in matches:
                links[url].append(p.concept.code)
        self.stdout.write("Found {} unique links".format(len(links)))

        for url, concepts in links.items():
            concepts = ",".join(concepts)
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)
                if r.history:
                    self.stdout.write(
                        "[WARN] {} for {} ==> {}, concepts:{}".format(
                            r.status_code, url, r.url, concepts
                        )
                    )
                if 200 <= r.status_code < 300:
                    self.stdout.write(
                        "[OK]   {} for {}, concepts = {}".format(
                            r.status_code, url, concepts
                        )
                    )
                elif 300 <= r.status_code < 400:
                    self.stdout.write(
                        "[WARN] {} for {} ==> {}, concepts:{}".format(
                            r.status_code, url, r.url, concepts
                        )
                    )
                elif r.status_code >= 400:
                    self.stderr.write(
                        "[ERR]  {} for {}, concepts:{}".format(
                            r.status_code, url, concepts
                        )
                    )
            except requests.exceptions.RequestException as e:
                self.stderr.write(
                    "[ERR] {} for {}, concepts:{}".format(e, url, concepts)
                )
