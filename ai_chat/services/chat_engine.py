"""Основной движок AI чата: RAG + Gemini + роутинг намерений."""

import logging
from django.conf import settings

from ai_core.models import AIContext
from ai_core.services.gemini_client import generate_text
from ai_core.services.embeddings import search_similar, search_news

logger = logging.getLogger('ai_chat')

# Системный промпт для чат-бота
SYSTEM_PROMPT_TEMPLATE = """Ты — умный AI-ассистент агрокомпании AgroStar (AgroTech). Ты помогаешь пользователям:

1. ПОИСК ПО САЙТУ — ищешь информацию в новостях, проектах, контактах компании
2. АГРОНОМИЧЕСКИЙ СОВЕТ — рекомендуешь что сажать на основе региона, почвы и целей пользователя
3. ПОМОЩЬ С ОБРАЩЕНИЯМИ — помогаешь составить обращение, контакт или заявку по проектам компании
4. СОСТАВЛЕНИЕ КОНТРАКТОВ — составляешь тексты контрактов и договоров по запросу

{admin_context}

ВАЖНЫЕ ПРАВИЛА:
- Когда даёшь агрономический совет — ОБЯЗАТЕЛЬНО в конце добавь блок:
  "🌾 Наша компания может помочь вам с этим!" и укажи релевантные проекты/услуги из контекста.
- Если есть релевантные новости в контексте — ссылайся на них.
- Если пользователь просит составить контракт/обращение — составь полный текст документа.
- Отвечай на том языке, на котором пишет пользователь.
- Будь полезным, информативным и дружелюбным.

Контекст из базы данных компании:
{rag_context}
"""


def _get_admin_context():
    """Загружает активные контексты от админа."""
    contexts = AIContext.objects.filter(is_active=True).order_by('priority')
    if not contexts.exists():
        return ''

    parts = ['Дополнительная информация от администрации:']
    for ctx in contexts:
        parts.append(f'[{ctx.title}]: {ctx.content}')

    return '\n'.join(parts)


def _get_rag_context(user_message, language='ru'):
    """Получает релевантный контекст из БД через RAG."""
    try:
        results = search_similar(user_message, top_k=5, language=language)
        if not results:
            return 'Релевантный контент не найден.'

        context_parts = []
        for doc in results:
            source_label = {
                'news': 'Новость',
                'project': 'Проект',
                'company_info': 'О компании',
                'partner': 'Партнёр',
                'certificate': 'Сертификат',
                'contact_info': 'Контакт',
            }.get(doc.source_type, doc.source_type)

            context_parts.append(
                f'[{source_label} #{doc.source_id}] {doc.content_title}\n{doc.content_text[:500]}'
            )

        return '\n\n'.join(context_parts)

    except Exception as e:
        logger.warning(f'Ошибка RAG поиска: {e}')
        return 'Контекст из базы данных временно недоступен.'


def _build_history(messages, max_messages=10):
    """Конвертирует ChatMessage в формат Gemini history."""
    history = []
    recent = messages[:max_messages]

    for msg in recent:
        role = 'user' if msg.role == 'user' else 'model'
        history.append({
            'role': role,
            'parts': [{'text': msg.content}]
        })

    return history


def _detect_language(text):
    """Простое определение языка по символам."""
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    latin = sum(1 for c in text if 'a' <= c.lower() <= 'z')

    if cyrillic > latin:
        return 'ru'
    return 'en'


def _find_related_projects(ai_response):
    """Ищет проекты, связанные с ответом ИИ."""
    from projects.models import Project

    projects = []
    try:
        for project in Project.objects.filter(is_current=True):
            try:
                project.set_current_language('ru')
                title = project.safe_translation_getter('title', default='') or ''
                description = project.safe_translation_getter('description', default='') or ''
                projects.append({
                    'id': project.pk,
                    'title': title,
                    'description': description[:200],
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f'Ошибка поиска проектов: {e}')

    return projects[:5]


def process_message(session, user_message):
    """Обрабатывает сообщение пользователя и генерирует ответ.

    Args:
        session: ChatSession
        user_message: Текст сообщения от пользователя

    Returns:
        dict: {
            'text': str,           # Ответ ИИ
            'pdf_url': str|None,   # URL PDF если был сгенерирован
            'sources': list,       # Источники из RAG
            'related_projects': list,  # Связанные проекты
        }
    """
    from ai_chat.models import ChatMessage

    # Определяем язык
    language = _detect_language(user_message)

    # Загружаем контексты
    admin_context = _get_admin_context()
    rag_context = _get_rag_context(user_message, language)

    # Формируем системный промпт
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        admin_context=admin_context,
        rag_context=rag_context,
    )

    # Собираем историю чата
    previous_messages = list(session.messages.all().order_by('-created_at')[:10])
    previous_messages.reverse()
    history = _build_history(previous_messages)

    # Генерируем ответ через Gemini
    ai_response = generate_text(
        prompt=user_message,
        system_instruction=system_prompt,
        history=history,
    )

    # Собираем источники из RAG результатов
    sources = []
    try:
        rag_results = search_similar(user_message, top_k=3, language=language)
        for doc in rag_results:
            sources.append({
                'type': doc.source_type,
                'id': doc.source_id,
                'title': doc.content_title,
            })
    except Exception:
        pass

    # Проверяем нужен ли PDF (контракт/обращение)
    pdf_url = None
    contract_keywords = ['контракт', 'договор', 'шартнома', 'contract', 'обращение', 'заявка', 'ариза']
    if any(kw in user_message.lower() for kw in contract_keywords):
        try:
            from .pdf import generate_contract_pdf
            pdf_url = generate_contract_pdf(ai_response, session)
        except Exception as e:
            logger.warning(f'Ошибка генерации PDF: {e}')

    # Находим связанные проекты
    related_projects = _find_related_projects(ai_response)

    # Сохраняем сообщения
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message,
    )

    metadata = {
        'sources': sources,
        'related_projects': related_projects,
    }
    if pdf_url:
        metadata['pdf_url'] = pdf_url

    ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=ai_response,
        metadata=metadata,
    )

    # Автоматически задаём заголовок сессии из первого сообщения
    if not session.title:
        session.title = user_message[:100]
        session.save(update_fields=['title'])

    return {
        'text': ai_response,
        'pdf_url': pdf_url,
        'sources': sources,
        'related_projects': related_projects,
    }
