from dataclasses import dataclass

@dataclass
class DocumentMetadata:
    title: str
    url: str
    technology: str
    category: str
    english_level: str
    professional_context: str
    content_type: str
    last_updated: str