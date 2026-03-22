"""Management command для индексации контента в эмбеддинги.

Использование:
    python manage.py index_embeddings              # Полная индексация
    python manage.py index_embeddings --model news  # Только новости
    python manage.py index_embeddings --language ru  # Только русский
    python manage.py index_embeddings --clear       # Очистить и переиндексировать
"""

from django.core.management.base import BaseCommand
from ai_core.models import DocumentEmbedding
from ai_core.services import indexer


class Command(BaseCommand):
    help = 'Индексация контента из БД в векторные эмбеддинги для RAG поиска'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['news', 'projects', 'company_info', 'partners', 'certificates', 'contact_info'],
            help='Индексировать только конкретную модель'
        )
        parser.add_argument(
            '--language',
            type=str,
            help='Индексировать только конкретный язык (ru, en, uz, kk)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все эмбеддинги перед индексацией'
        )

    def handle(self, *args, **options):
        model = options.get('model')
        language = options.get('language')
        clear = options.get('clear', False)
        languages = [language] if language else None

        if clear:
            count = DocumentEmbedding.objects.count()
            DocumentEmbedding.objects.all().delete()
            self.stdout.write(f'Удалено {count} эмбеддингов.')

        # Карта: аргумент → функция индексации
        index_map = {
            'news': lambda: indexer.index_news(languages),
            'projects': lambda: indexer.index_projects(languages),
            'company_info': lambda: indexer.index_company_info(languages),
            'partners': lambda: indexer.index_partners(languages),
            'certificates': lambda: indexer.index_certificates(),
            'contact_info': lambda: indexer.index_contact_info(languages),
        }

        if model:
            self.stdout.write(f'Индексация: {model}...')
            count = index_map[model]()
        else:
            self.stdout.write('Полная индексация всех моделей...')
            count = indexer.index_all(languages)

        self.stdout.write(self.style.SUCCESS(f'Готово! Проиндексировано записей: {count}'))
