import re
def highlight_text(text):
    text_format = re.sub(
        r'\*\*(.*?)\*\*',
        r'<span style="color: coral; padding: 0.1rem 0.3rem;">\1</span>',
        text)

    text_format = re.sub(
        r'\*(.*?)\*',
        r'<em style="color:coral;">\1</em>',
        text_format
    )   

    return text_format    