"""Обёртка над Google Gemini API для чата и эмбеддингов."""

import logging
from django.conf import settings
from google import genai

logger = logging.getLogger('ai_core')

# Инициализируем клиент Gemini
_client = None


def get_client():
    """Ленивая инициализация клиента Gemini."""
    global _client
    if _client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError('GEMINI_API_KEY не настроен в .env файле')
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(prompt, system_instruction=None, history=None):
    """Генерация текста через Gemini.

    Args:
        prompt: Текст запроса пользователя
        system_instruction: Системный промпт
        history: Список предыдущих сообщений [{'role': 'user'|'model', 'parts': [{'text': '...'}]}]

    Returns:
        Текст ответа от Gemini
    """
    client = get_client()

    # Собираем содержимое
    contents = []
    if history:
        contents.extend(history)

    contents.append({
        'role': 'user',
        'parts': [{'text': prompt}]
    })

    config = {}
    if system_instruction:
        config['system_instruction'] = system_instruction

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config,
        )
        return response.text
    except Exception as e:
        logger.error(f'Ошибка Gemini generate_text: {e}')
        raise


def generate_embedding(text):
    """Генерация эмбеддинга для текста.

    Args:
        text: Текст для эмбеддинга

    Returns:
        Список float значений (768 размерность)
    """
    client = get_client()

    try:
        result = client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=text,
        )
        return result.embeddings[0].values
    except Exception as e:
        logger.error(f'Ошибка Gemini generate_embedding: {e}')
        raise


def generate_embeddings_batch(texts):
    """Пакетная генерация эмбеддингов.

    Args:
        texts: Список текстов

    Returns:
        Список эмбеддингов (каждый — список float)
    """
    client = get_client()

    try:
        result = client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=texts,
        )
        return [emb.values for emb in result.embeddings]
    except Exception as e:
        logger.error(f'Ошибка Gemini batch embedding: {e}')
        raise
