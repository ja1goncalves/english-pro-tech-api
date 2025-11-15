import re
from typing import Tuple

from app.exception.exception import GenAIError, RAGError
from app.model.entity import UserBase, Role, RoleLevel, RolePlay, UserPlayStory, RAGDocument
from app.service.rag_chuck_service import RagChunkService
from app.service.rag_doc_service import RagDocService
from app.util.chunk import translate_context_chunk
from app.util.role_play import story_play_str
from app.model.dto import RoleDTO, RoleLevelDTO, RolePlayDTO
from resource.agent_ai.gen_ai_api import GenAIAPI
from resource.rag_system.data_class.processed_chunk import ProcessedChunk
from resource.rag_system.tech_english_rag_system import TechEnglishRAGSystem


class GenIAService:

    def __init__(self, db, user: UserBase):
        self.db = db
        self.system_message = f"""You are an AI conversation assistant specializing in creating practical challenges,
        in chat format (like talking), to help users improve their technical English skills. My name is {user.name} and 
        I am at the {user.level} level of development in technology. Consider my development level and the proposed
        challenge to create a suitable challenge or continue an existing as a natural conversation."""
        self.gen_ia = GenAIAPI(self.system_message)

    async def get_context_rag(self, question: str, n_results: int = 5, translate: bool = True) -> str | dict:
        rag_chunk_service = RagChunkService(self.db)
        chunks = await rag_chunk_service.all(limit=5000)
        processed_chunks = [ProcessedChunk(**chunk) for chunk in chunks]

        if not chunks:
            rag_doc_service = RagDocService(self.db)
            docs = await rag_doc_service.all(limit=5000)
        else:
            docs = []

        rag_system = await TechEnglishRAGSystem.create_and_setup(processed_chunks, docs)
        if not rag_system.vector_store or not rag_system.chunks:
            raise RAGError("RAG system is not properly configured.")

        results = rag_system.query_rag(question, context="development", n_results=n_results)

        if not results["success"] or not results['context_chunks']:
            raise RAGError(results.get("error", "Unknown RAG error."))

        return translate_context_chunk(results['context_chunks']) if translate else results['context_chunks']

    async def init_play(self, role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                        task: RolePlayDTO | RolePlay) -> Tuple[int, str, str]:
        role_name = role.name
        step = level.step
        challenge = task.challenge
        description = task.description or "Explore relevant technical points."
        metadata = task.metadata
        rag_context: str = await self.get_context_rag(challenge, 3, True)

        question = f"""Please create a custom practical challenge for the {role_name} development role from the
        technical level {step}, where {challenge} is {description} so that I can improve my skills in technical English."""
        context = f"""Use the following additional information to make the challenge more relevant:
        - Metadata: {metadata}
        - Technical Context: {rag_context}"""

        try:
            prompt = f"{question}\n{context}"
            return 0, question, self.gen_ia.send_prompt(prompt)
        except Exception as e:
            raise GenAIError(e.__str__())

    async def answer_play(self, answer: str, story: list[UserPlayStory],
                          role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                          task: RolePlayDTO | RolePlay) -> Tuple[int, str, str]:
        role_name = role.name
        step = level.step
        challenge = task.challenge
        description = task.description or "Explore relevant technical points."
        metadata = task.metadata
        rag_context: str = await self.get_context_rag(f"{challenge}: {answer}.", 5, True)

        question = f"""Knowing that I'm at the {role_name} development role from technical level {step} in the
        '{challenge}' challenge where {description} so that I can improve my skills in technical English and that
        I have already had the following progress story in the challenges inside in the field 'Chat Story'.
        My reply to the practice challenge is: "{answer}". Please provide a detailed, but also direct, feedback,
        as a dialog replay, on my answer, highlighting strengths and areas for improvement, and suggest ways to improve
        their technical English skills based on the answer provided."""
        point_structure = f"""Based on the answer, evaluate and assign an appropriate XP score between 0 and {task.xp}
        in the format 'Points=20xp' at the beginning of the feedback. Like this example:
        'Points=15xp. Your answer demonstrates...'."""
        context = f"""Use the following additional information to make the challenge more relevant:
        - Metadata: {metadata}
        - Chat Story: {story_play_str(story)}
        - Technical Context: {rag_context}"""

        try:
            prompt = f"{question}\n{point_structure}\n{context}"
            res = self.gen_ia.send_prompt(prompt)

            regex_xp = r'Points=(\d+)xp'
            get_points = re.search(regex_xp, res)
            xp = round((int(get_points.group(1)) if get_points else task.xp) / 3)

            res = re.sub(regex_xp, "", res)

            return xp, question, res
        except Exception as e:
            raise GenAIError(e.__str__())


