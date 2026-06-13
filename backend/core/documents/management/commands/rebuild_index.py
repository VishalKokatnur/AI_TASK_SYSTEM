from django.core.management.base import BaseCommand
from documents.ai_search import rebuild_index_from_db

class Command(BaseCommand):
    help = 'Rebuild the FAISS search index from all documents in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Rebuilding FAISS index...')
        rebuild_index_from_db()
        self.stdout.write(self.style.SUCCESS('Index rebuilt successfully!'))