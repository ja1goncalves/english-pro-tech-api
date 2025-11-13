from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ProcessedChunk:
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    embedding: List[float] = None