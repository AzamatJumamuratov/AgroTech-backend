"""Генерация эмбеддингов и поиск по pgvector."""

import logging
from pgvector.django import CosineDistance
from ai_core.models import DocumentEmbedding
from .gemini_client import generate_embedding

logger = logging.getLogger('ai_core')


def search_similar(query_text, top_k=5, language=None, source_types=None):
    """Семантический поиск по эмбеддингам.

    Args:
        query_text: Текст запроса
        top_k: Количество результатов
        language: Фильтр по языку (None = все)
        source_types: Фильтр по типам источников ['news', 'project', ...]

    Returns:
        QuerySet с результатами, отсортированными по релевантности
    """
    # Генерируем эмбеддинг для запроса
    query_embedding = generate_embedding(query_text)

    # Строим запрос
    qs = DocumentEmbedding.objects.all()

    if language:
        qs = qs.filter(language=language)

    if source_types:
        qs = qs.filter(source_type__in=source_types)

    # Поиск по косинусному расстоянию
    results = qs.order_by(
        CosineDistance('embedding', query_embedding)
    )[:top_k]

    return results


def search_news(query_text, top_k=5, language=None):
    """Поиск только по новостям."""
    return search_similar(
        query_text,
        top_k=top_k,
        language=language,
        source_types=['news'],
    )
