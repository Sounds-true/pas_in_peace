"""
API endpoints для AI Quest Builder
Adapted from inner_edu for pas_in_peace (Integer IDs)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.storage import get_db
from src.storage.models import QuestBuilderSession, User
from src.quest_builder import QuestBuilderAgent, QuestGraph, ConversationStage

router = APIRouter()


class ChatRequest(BaseModel):
    """Запрос для chat endpoint"""
    user_id: int
    message: str
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Ответ от chat endpoint"""
    ai_response: str
    stage: str
    session_id: int
    graph: Optional[Dict] = None


class GenerateGraphRequest(BaseModel):
    """Запрос для генерации графа"""
    session_id: int
    force: bool = False


class RefineNodeRequest(BaseModel):
    """Запрос для улучшения узла"""
    session_id: int
    node_id: str
    user_feedback: str


# Инициализация агента (singleton)
quest_builder_agent = QuestBuilderAgent()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_builder(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Чат с AI Quest Builder

    Flow:
    1. Если session_id не указан - создаем новую сессию
    2. Загружаем историю диалога из БД
    3. Обрабатываем сообщение через QuestBuilderAgent
    4. Сохраняем обновленную историю
    5. Возвращаем ответ AI (+ граф если сгенерирован)
    """
    try:
        # Получить или создать сессию
        if request.session_id:
            result = await db.execute(
                select(QuestBuilderSession).where(QuestBuilderSession.id == request.session_id)
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            # Создать новую сессию
            session = QuestBuilderSession(
                user_id=request.user_id,
                conversation_history=[],
                current_stage=ConversationStage.GREETING,
                quest_context={}
            )
            db.add(session)
            await db.flush()  # Получить ID сессии

        # Обработать сообщение через агента
        ai_response, new_stage, quest_graph = await quest_builder_agent.chat(
            user_message=request.message,
            conversation_history=session.conversation_history,
            current_stage=session.current_stage,
            quest_context=session.quest_context
        )

        # Обновить сессию
        session.current_stage = new_stage
        # conversation_history уже обновлен агентом (pass by reference)

        # Если сгенерирован граф
        if quest_graph:
            session.current_graph = quest_graph.model_dump()

        await db.commit()

        # Ответ
        return ChatResponse(
            ai_response=ai_response,
            stage=new_stage,
            session_id=session.id,
            graph=session.current_graph
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить историю диалога и текущий граф"""
    try:
        result = await db.execute(
            select(QuestBuilderSession).where(QuestBuilderSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "conversation_history": session.conversation_history,
            "current_stage": session.current_stage,
            "current_graph": session.current_graph,
            "quest_context": session.quest_context
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_graph")
async def generate_graph(
    request: GenerateGraphRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Принудительная генерация графа из текущего контекста

    Используется если родитель хочет сгенерировать граф сейчас,
    не дожидаясь естественного flow
    """
    try:
        result = await db.execute(
            select(QuestBuilderSession).where(QuestBuilderSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Установить стадию на GENERATING
        session.current_stage = ConversationStage.GENERATING

        # Вызвать chat с пустым сообщением (агент сгенерирует граф)
        ai_response, new_stage, quest_graph = await quest_builder_agent.chat(
            user_message="Сгенерируй квест",
            conversation_history=session.conversation_history,
            current_stage=ConversationStage.GENERATING,
            quest_context=session.quest_context
        )

        if quest_graph:
            session.current_graph = quest_graph.model_dump()
            session.current_stage = new_stage
            await db.commit()

            return {
                "success": True,
                "graph": session.current_graph
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Недостаточно информации для генерации квеста. Ответь на вопросы AI."
            )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine_node")
async def refine_node(
    request: RefineNodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Улучшить конкретный узел графа через AI"""
    try:
        result = await db.execute(
            select(QuestBuilderSession).where(QuestBuilderSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()

        if not session or not session.current_graph:
            raise HTTPException(status_code=404, detail="Session or graph not found")

        # Конвертируем dict в QuestGraph
        current_graph = QuestGraph(**session.current_graph)

        # Улучшить узел
        updated_node = await quest_builder_agent.refine_node(
            node_id=request.node_id,
            user_feedback=request.user_feedback,
            current_graph=current_graph
        )

        # Обновить узел в графе
        for i, node in enumerate(current_graph.nodes):
            if node.id == request.node_id:
                current_graph.nodes[i] = updated_node
                break

        # Сохранить
        session.current_graph = current_graph.model_dump()
        await db.commit()

        return {
            "success": True,
            "updated_node": updated_node.model_dump()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{session_id}")
async def reset_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Сбросить сессию (начать заново)"""
    try:
        result = await db.execute(
            select(QuestBuilderSession).where(QuestBuilderSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Сброс
        session.conversation_history = []
        session.current_stage = ConversationStage.GREETING
        session.current_graph = None
        session.quest_context = {}

        await db.commit()

        return {"success": True, "message": "Session reset"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save_quest")
async def save_quest(
    session_id: int,
    title: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Сохранить квест из сессии в таблицу quests

    После финализации квеста родитель может сохранить его
    """
    try:
        # Получить сессию
        result = await db.execute(
            select(QuestBuilderSession).where(QuestBuilderSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session or not session.current_graph:
            raise HTTPException(status_code=404, detail="Session or graph not found")

        # Импортируем Quest модель
        from src.storage.models import Quest, ModerationStatusEnum, QuestStatusEnum
        import uuid

        # Создать Quest
        quest = Quest(
            user_id=session.user_id,
            quest_id=str(uuid.uuid4()),
            title=title,
            description=session.quest_context.get("topic", ""),
            child_name=session.quest_context.get("child_name"),
            child_age=session.quest_context.get("age"),
            child_interests=session.quest_context.get("interests", []),
            graph_structure=session.current_graph,  # PRIMARY storage
            quest_yaml="",  # TODO: Generate from graph
            total_nodes=len(session.current_graph.get("nodes", [])),
            difficulty_level=session.quest_context.get("difficulty", "medium"),
            psychological_module=session.quest_context.get("psychological_module"),
            location=session.quest_context.get("location"),
            age_range=session.quest_context.get("age_range"),
            status=QuestStatusEnum.DRAFT,
            moderation_status=ModerationStatusEnum.PENDING
        )

        db.add(quest)
        await db.commit()
        await db.refresh(quest)

        return {
            "success": True,
            "quest_id": quest.id,
            "message": "Quest saved successfully"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
