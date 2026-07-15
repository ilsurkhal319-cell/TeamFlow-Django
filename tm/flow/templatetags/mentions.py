import re
from django import template

register = template.Library()


@register.filter
def render_mentions(text):
    """Заменяет @username на красиво отформатированный HTML"""
    if not text:
        return ''

    # Паттерн для поиска @username
    pattern = r'@(\w+)'

    def replace_mention(match):
        username = match.group(1)
        return f'<span class="text-violet-400 font-medium mention">@{username}</span>'

    return re.sub(pattern, replace_mention, text)


@register.filter
def parse_mentions(text):
    """Извлекает список username из текста"""
    if not text:
        return []

    pattern = r'@(\w+)'
    return re.findall(pattern, text)