"""Индексация контента из БД в эмбеддинги для RAG поиска."""

import logging
from django.conf import settings
from ai_core.models import DocumentEmbedding
from .gemini_client import generate_embedding

logger = logging.getLogger('ai_core')

# Языки для индексации translatable моделей
LANGUAGES = [lang[0] for lang in settings.LANGUAGES]


def _index_translatable_model(model_class, source_type, text_builder, languages=None):
    """Индексирует TranslatableModel.

    Args:
        model_class: Класс модели (News, Project, и т.д.)
        source_type: Строка типа ('news', 'project', ...)
        text_builder: Функция (obj, lang) -> (title, text) для извлечения текста
        languages: Список языков для индексации
    """
    langs = languages or LANGUAGES
    count = 0

    for obj in model_class.objects.all():
        for lang in langs:
            try:
                obj.set_current_language(lang)
                title, text = text_builder(obj, lang)

                if not text or not text.strip():
                    continue

                embedding = generate_embedding(text)

                DocumentEmbedding.objects.update_or_create(
                    source_type=source_type,
                    source_id=obj.pk,
                    language=lang,
                    defaults={
                        'content_text': text,
                        'content_title': title,
                        'embedding': embedding,
                    }
                )
                count += 1
                logger.info(f'  [{source_type}:{obj.pk}:{lang}] {title[:50]}')

            except Exception as e:
                logger.warning(f'  Пропущено [{source_type}:{obj.pk}:{lang}]: {e}')
                continue

    return count


def _index_simple_model(model_class, source_type, text_builder, language='ru'):
    """Индексирует обычную модель (не translatable)."""
    count = 0

    for obj in model_class.objects.all():
        try:
            title, text = text_builder(obj)

            if not text or not text.strip():
                continue

            embedding = generate_embedding(text)

            DocumentEmbedding.objects.update_or_create(
                source_type=source_type,
                source_id=obj.pk,
                language=language,
                defaults={
                    'content_text': text,
                    'content_title': title,
                    'embedding': embedding,
                }
            )
            count += 1
            logger.info(f'  [{source_type}:{obj.pk}] {title[:50]}')

        except Exception as e:
            logger.warning(f'  Пропущено [{source_type}:{obj.pk}]: {e}')
            continue

    return count


def index_news(languages=None):
    """Индексация новостей."""
    from news.models import News
    logger.info('Индексация новостей...')

    def builder(obj, lang):
        title = obj.safe_translation_getter('title', default='') or ''
        content = obj.safe_translation_getter('content', default='') or ''
        text = f"{title}\n{content}".strip()
        return title, text

    return _index_translatable_model(News, 'news', builder, languages)


def index_projects(languages=None):
    """Индексация проектов."""
    from projects.models import Project
    logger.info('Индексация проектов...')

    def builder(obj, lang):
        title = obj.safe_translation_getter('title', default='') or ''
        description = obj.safe_translation_getter('description', default='') or ''
        text = f"{title}\n{description}".strip()
        return title, text

    return _index_translatable_model(Project, 'project', builder, languages)


def index_company_info(languages=None):
    """Индексация информации о компании."""
    from core.models import CompanyInfo
    logger.info('Индексация CompanyInfo...')

    def builder(obj, lang):
        title = obj.safe_translation_getter('title', default='') or ''
        description = obj.safe_translation_getter('description', default='') or ''
        text = f"{title}\n{description}".strip()
        return title, text

    return _index_translatable_model(CompanyInfo, 'company_info', builder, languages)


def index_partners(languages=None):
    """Индексация партнёров."""
    from core.models import Partner
    logger.info('Индексация партнёров...')

    def builder(obj, lang):
        name = obj.safe_translation_getter('name', default='') or ''
        description = obj.safe_translation_getter('description', default='') or ''
        text = f"{name}\n{description}".strip()
        return name, text

    return _index_translatable_model(Partner, 'partner', builder, languages)


def index_certificates():
    """Индексация сертификатов."""
    from core.models import Certificate
    logger.info('Индексация сертификатов...')

    def builder(obj):
        return obj.caption, obj.caption

    return _index_simple_model(Certificate, 'certificate', builder)


def index_contact_info(languages=None):
    """Индексация контактной информации."""
    from core.models import ContactInfo
    logger.info('Индексация ContactInfo...')

    def builder(obj, lang):
        address = obj.safe_translation_getter('address', default='') or ''
        text = f"Email: {obj.email} Телефон: {obj.phone} Адрес: {address}".strip()
        return 'Контактная информация', text

    return _index_translatable_model(ContactInfo, 'contact_info', builder, languages)


def index_all(languages=None):
    """Полная индексация всего контента."""
    total = 0
    logger.info('=== Начинаем полную индексацию ===')

    total += index_news(languages)
    total += index_projects(languages)
    total += index_company_info(languages)
    total += index_partners(languages)
    total += index_certificates()
    total += index_contact_info(languages)

    logger.info(f'=== Индексация завершена. Всего записей: {total} ===')
    return total
