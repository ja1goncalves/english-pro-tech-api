from dataclasses import dataclass

@dataclass
class GitHubDocMetadata:
    title: str
    url: str
    repo: str
    file_path: str
    file_type: str
    technology: str
    professional_context: str
    english_level: str
    content_type: str
    last_updated: str