import json
import time
import uuid
from typing import Optional

from open_webui.apps.webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text

####################
# Knowledge bases DB Schema
####################

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by_user_id = Column(String)
    title = Column(String)
    description = Column(Text)
    embedding_model = Column(String)
    type = Column(String) # general or scrape websites
    documents = Column(String) 

    created_at = Column(BigInteger, default=time.time)
    updated_at = Column(BigInteger, default=time.time)

class KnowledgeBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_user_id: str
    title: str
    description: str
    embedding_model: str
    type: str
    documents: str

    created_at: int
    updated_at: int

####################
# Forms
####################

class KnowledgeBaseForm(BaseModel):
    title: str
    description: str
    embedding_model: str
    type: str
    documents: list[dict] = []

class KnowledgeBaseResponse(BaseModel):
    id: str
    title: str

class KnowledgeBaseFullResponse(BaseModel):
    id: str
    title: str
    description: str
    embedding_model: str
    type: str
    documents: list[dict]

class KnowledgeBaseTable:
    def insert_new_knowledge_base(self, form_data: KnowledgeBaseForm, user_id: str):
        with get_db() as db:
            id = str(uuid.uuid4())

            new_kb = KnowledgeBaseModel(
                id=id,
                created_by_user_id=user_id,
                title=form_data.title,
                description=form_data.description,
                embedding_model=form_data.embedding_model,
                type=form_data.type,
                documents=json.dumps(form_data.documents),
                created_at=int(time.time()),
                updated_at=int(time.time())
            )

            result = KnowledgeBase(**new_kb.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return KnowledgeBaseModel.model_validate(result) if result else None
        
    def get_all_knowledge_bases(self) -> list[KnowledgeBaseModel]:
        with get_db() as db:
            query = db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()
            return [KnowledgeBaseModel.model_validate(kb) for kb in query]
        
    def get_knowledge_base_by_id(self, id: str) -> Optional[KnowledgeBaseModel]:
        with get_db() as db:
            kb = db.query(KnowledgeBase).filter_by(id=id).first()
            return KnowledgeBaseModel.model_validate(kb) if kb else None
        
    def update_knowledge_base_by_id(self, id: str, form_data: KnowledgeBaseForm) -> Optional[KnowledgeBaseModel]:
        try:
            with get_db() as db:
                kb = db.get(KnowledgeBase, id)
                kb.title = form_data.title
                kb.description = form_data.description
                kb.embedding_model = form_data.embedding_model
                kb.type = form_data.type
                kb.documents = json.dumps(form_data.documents)
                kb.updated_at = int(time.time())
                db.commit()
                db.refresh(kb)
                return KnowledgeBaseModel.model_validate(kb)
        except Exception:
            return None
        
    def delete_knowledge_base_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(KnowledgeBase).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

KnowledgeBases = KnowledgeBaseTable()