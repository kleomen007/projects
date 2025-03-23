import re
from filters.word import words

# Регулярные выражения для поиска ссылок и каналов
url_pattern = r'https?://\S+'
channel_pattern = r'@[\w]+'

def check_text(text: str) -> bool:
    # Проверка на 18+ слова
    adult_content_found = any(word in text.lower() for word in words)
    
    # Проверка на ссылки
    links_found = bool(re.search(url_pattern, text))
    
    # Проверка на каналы (например, Telegram)
    channels_found = bool(re.search(channel_pattern, text))
    
    # Если найдены 18+ слова или ссылки
    if adult_content_found or links_found or channels_found:
        return False
    return True