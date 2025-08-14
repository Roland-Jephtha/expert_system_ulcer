import os

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'chat', 'knowledge.txt')

def load_knowledge_base():
    with open(KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
        entries = [line.strip() for line in f if line.strip()]
    return entries
