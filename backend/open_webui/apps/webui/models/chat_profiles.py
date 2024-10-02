import json
import time
import uuid
from typing import Optional

from open_webui.apps.webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text

####################
# Chat Profiles DB Schema
####################

class ChatProfile(Base):
    __tablename__ = "chat_profile"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by_user_id = Column(String)
    title = Column(String)
    description = Column(Text)
    llm_model = Column(String)
    roles_allowed = Column(String) 
    knowledge_bases = Column(String)
    enabled = Column(Boolean, default=True)
    params = Column(Text)

    created_at = Column(BigInteger, default=time.time)
    updated_at = Column(BigInteger, default=time.time)
    

class ChatProfileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_user_id: str
    title: str
    description: str
    llm_model: str
    roles_allowed: str
    knowledge_bases: str
    enabled: bool
    params: str

    created_at: int
    updated_at: int


####################
# Forms
####################

class ChatProfileForm(BaseModel):
    title: str
    description: str = ""
    llm_model: str = ""
    roles_allowed: list[str] = []
    knowledge_bases: list[str] = [] 
    enabled: bool = True
    params: dict = {}

class ChatProfileFullResponse(BaseModel):
    id: str
    title: str
    description: str
    llm_model: str
    roles_allowed: list[str] = []
    knowledge_bases: list[str] = [] 
    enabled: bool
    params: dict

class ChatProfileResponse(BaseModel):
    id: str
    title: str

class ChatProfileTable:
    def insert_new_chat_profile(self, user_id: str, form_data: ChatProfileForm) -> Optional[ChatProfileModel]:
        with get_db() as db:
            id = str(uuid.uuid4())

            chat_profile = ChatProfileModel(
                id=id,
                created_by_user_id=user_id,
                title=form_data.title,
                description=form_data.description,
                llm_model=form_data.llm_model,
                roles_allowed=json.dumps(form_data.roles_allowed),
                knowledge_bases=json.dumps(form_data.knowledge_bases),
                enabled=form_data.enabled,
                params=json.dumps(form_data.params),
                created_at=int(time.time()),
                updated_at=int(time.time())
            )

            result = ChatProfile(**chat_profile.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return ChatProfileModel.model_validate(result) if result else None
        
    def get_all_chat_profiles(self) -> list[ChatProfileModel]:
        with get_db() as db:
            query = db.query(ChatProfile).order_by(ChatProfile.created_at.desc()).all()
            return [ChatProfileModel.model_validate(result) for result in query]
        
    def get_all_enabled_chat_profiles(self) -> list[ChatProfileModel]:
        with get_db() as db:
            query = db.query(ChatProfile).filter(ChatProfile.enabled == True).all()
            return [ChatProfileModel.model_validate(result) for result in query]
        
    def get_filtered_chat_profiles_by_role(self, user_role: str) -> list[ChatProfileModel]:
        with get_db() as db:
            query = db.query(ChatProfile).filter(ChatProfile.roles_allowed.contains(user_role)).all()
            return [ChatProfileModel.model_validate(result) for result in query]
        
    def get_filtered_enabled_chat_profiles_by_role(self, user_role: str) -> list[ChatProfileModel]:
        with get_db() as db:
            query = db.query(ChatProfile).filter(ChatProfile.roles_allowed.contains(user_role)).filter(ChatProfile.enabled == True).all()
            return [ChatProfileModel.model_validate(result) for result in query]
        
    def remove_kb_from_chat_profiles(self, kb_id: str) -> bool:
        try:
            with get_db() as db:
                profiles = db.query(ChatProfile).filter(ChatProfile.knowledge_bases.contains(kb_id)).all()
                for profile in profiles:
                    profile.knowledge_bases = json.dumps([id for id in json.loads(profile.knowledge_bases) if id != kb_id])
                    db.commit()
                    db.refresh(profile)
                return True
        except Exception:
            return False
        
    def get_chat_profile_by_id(self, id: str) -> Optional[ChatProfileModel]:
        try:
            with get_db() as db:
                chat_profile = db.get(ChatProfile, id)
                return ChatProfileModel.model_validate(chat_profile)
        except Exception:
            return None
        
    def update_chat_profile_by_id(self, id: str, form_data: ChatProfileForm) -> Optional[ChatProfileModel]:
        try:
            with get_db() as db:
                chat_profile = db.get(ChatProfile, id)
                chat_profile.title = form_data.title
                chat_profile.description = form_data.description
                chat_profile.llm_model = form_data.llm_model
                chat_profile.roles_allowed = json.dumps(form_data.roles_allowed)
                chat_profile.knowledge_bases = json.dumps(form_data.knowledge_bases)
                chat_profile.enabled = form_data.enabled
                chat_profile.params = json.dumps(form_data.params)
                chat_profile.updated_at = int(time.time())
                db.commit()
                db.refresh(chat_profile)
                return ChatProfileModel.model_validate(chat_profile)
        except Exception:
            return None
        
    def delete_chat_profile_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(ChatProfile).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False

ChatProfiles = ChatProfileTable()