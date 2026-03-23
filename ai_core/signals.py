"""Django сигналы для автоматического обновления эмбеддингов.

При создании/обновлении новостей, проектов, компании, партнёров —
автоматически пересоздаём эмбеддинг в фоне.
"""

import logging
import threading

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger('ai_core')


def _update_embedding_async(source_type, source_id):
    """Обновляет эмбеддинг в отдельном потоке чтобы не блокировать запрос."""

    def _do_update():
        try:
            from ai_core.services.indexer import (
                index_news, index_projects, index_company_info,
                index_partners, index_certificates, index_contact_info,
            )
            from ai_core.models import DocumentEmbedding

            # Карта: source_type → функция для одного объекта
            # Для простоты — переиндексируем все записи этого типа
            # (при малом кол-ве данных это быстро)
            indexer_map = {
                'news': index_news,
                'project': index_projects,
                'company_info': index_company_info,
                'partner': index_partners,
                'certificate': index_certificates,
                'contact_info': index_contact_info,
            }

            func = indexer_map.get(source_type)
            if func:
                logger.info(f'Авто-обновление эмбеддинга: {source_type}:{source_id}')
                func()

        except Exception as e:
            logger.warning(f'Ошибка авто-обновления эмбеддинга [{source_type}:{source_id}]: {e}')

    thread = threading.Thread(target=_do_update, daemon=True)
    thread.start()


def _delete_embedding(source_type, source_id):
    """Удаляет эмбеддинги при удалении исходного объекта."""
    try:
        from ai_core.models import DocumentEmbedding
        deleted, _ = DocumentEmbedding.objects.filter(
            source_type=source_type,
            source_id=source_id,
        ).delete()
        if deleted:
            logger.info(f'Удалены эмбеддинги: {source_type}:{source_id} ({deleted} шт.)')
    except Exception as e:
        logger.warning(f'Ошибка удаления эмбеддинга [{source_type}:{source_id}]: {e}')


# === Сигналы для News ===

@receiver(post_save, sender='news.News')
def on_news_save(sender, instance, **kwargs):
    _update_embedding_async('news', instance.pk)


@receiver(post_delete, sender='news.News')
def on_news_delete(sender, instance, **kwargs):
    _delete_embedding('news', instance.pk)


# === Сигналы для Project ===

@receiver(post_save, sender='projects.Project')
def on_project_save(sender, instance, **kwargs):
    _update_embedding_async('project', instance.pk)


@receiver(post_delete, sender='projects.Project')
def on_project_delete(sender, instance, **kwargs):
    _delete_embedding('project', instance.pk)


# === Сигналы для CompanyInfo ===

@receiver(post_save, sender='core.CompanyInfo')
def on_company_info_save(sender, instance, **kwargs):
    _update_embedding_async('company_info', instance.pk)


@receiver(post_delete, sender='core.CompanyInfo')
def on_company_info_delete(sender, instance, **kwargs):
    _delete_embedding('company_info', instance.pk)


# === Сигналы для Partner ===

@receiver(post_save, sender='core.Partner')
def on_partner_save(sender, instance, **kwargs):
    _update_embedding_async('partner', instance.pk)


@receiver(post_delete, sender='core.Partner')
def on_partner_delete(sender, instance, **kwargs):
    _delete_embedding('partner', instance.pk)


# === Сигналы для Certificate ===

@receiver(post_save, sender='core.Certificate')
def on_certificate_save(sender, instance, **kwargs):
    _update_embedding_async('certificate', instance.pk)


@receiver(post_delete, sender='core.Certificate')
def on_certificate_delete(sender, instance, **kwargs):
    _delete_embedding('certificate', instance.pk)


# === Сигналы для ContactInfo ===

@receiver(post_save, sender='core.ContactInfo')
def on_contact_info_save(sender, instance, **kwargs):
    _update_embedding_async('contact_info', instance.pk)


@receiver(post_delete, sender='core.ContactInfo')
def on_contact_info_delete(sender, instance, **kwargs):
    _delete_embedding('contact_info', instance.pk)
