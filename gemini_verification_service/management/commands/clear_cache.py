from django.core.management.base import BaseCommand # type: ignore
from django.core.cache import cache # type: ignore

class Command(BaseCommand):
    help = 'Clears the cache'

    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cache cleared successfully'))