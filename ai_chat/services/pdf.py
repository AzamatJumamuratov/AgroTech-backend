"""Генерация PDF документов (контракты, обращения)."""

import os
import uuid
from datetime import datetime

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import logging

logger = logging.getLogger('ai_chat')

# Директория для PDF файлов
PDF_DIR = os.path.join(settings.MEDIA_ROOT, 'contracts')

# Путь к шрифту с поддержкой кириллицы
FONT_PATH = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
FONT_BOLD_PATH = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans-Bold.ttf')

_fonts_registered = False


def _register_fonts():
    """Регистрация шрифтов с поддержкой кириллицы."""
    global _fonts_registered
    if _fonts_registered:
        return

    try:
        if os.path.exists(FONT_PATH):
            pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', FONT_BOLD_PATH))
        _fonts_registered = True
    except Exception as e:
        logger.warning(f'Не удалось зарегистрировать шрифты: {e}')


def _get_styles():
    """Стили для PDF документа."""
    _register_fonts()

    styles = getSampleStyleSheet()

    # Определяем шрифт — DejaVuSans если доступен, иначе Helvetica
    font_name = 'DejaVuSans' if _fonts_registered else 'Helvetica'
    font_bold = 'DejaVuSans-Bold' if _fonts_registered else 'Helvetica-Bold'

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName=font_bold,
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # CENTER
    ))

    styles.add(ParagraphStyle(
        name='DocBody',
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name='DocFooter',
        fontName=font_name,
        fontSize=9,
        textColor='#888888',
        alignment=1,
    ))

    return styles


def generate_contract_pdf(contract_text, session):
    """Генерирует PDF документ с текстом контракта.

    Args:
        contract_text: Текст контракта/обращения от ИИ
        session: ChatSession

    Returns:
        str: URL для скачивания PDF (относительный)
    """
    os.makedirs(PDF_DIR, exist_ok=True)

    # Генерируем уникальное имя файла
    filename = f"doc_{session.pk}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(PDF_DIR, filename)

    styles = _get_styles()

    # Создаём PDF
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    elements = []

    # Заголовок
    elements.append(Paragraph('AgroStar', styles['DocTitle']))
    elements.append(Spacer(1, 12))

    # Текст документа — разбиваем по абзацам
    paragraphs = contract_text.split('\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            elements.append(Spacer(1, 8))
            continue

        # Экранируем HTML-символы для ReportLab
        para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Жирный текст для строк начинающихся с ** или #
        if para.startswith('**') or para.startswith('#'):
            para = para.strip('*# ')
            elements.append(Paragraph(f'<b>{para}</b>', styles['DocBody']))
        else:
            elements.append(Paragraph(para, styles['DocBody']))

    # Футер
    elements.append(Spacer(1, 30))
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    elements.append(Paragraph(
        f'Документ сгенерирован: {now} | AgroStar AI Assistant',
        styles['DocFooter']
    ))

    doc.build(elements)

    # Возвращаем URL для скачивания
    return f'{settings.MEDIA_URL}contracts/{filename}'
