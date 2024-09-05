import uuid
from open_webui.config import BannerModel
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from open_webui.utils.utils import get_admin_user, get_verified_user

from open_webui.config import get_config, save_config

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status

router = APIRouter()


############################
# ImportConfig
############################


class ImportConfigForm(BaseModel):
    config: dict


@router.post("/import", response_model=dict)
async def import_config(form_data: ImportConfigForm, user=Depends(get_admin_user)):
    save_config(form_data.config)
    return get_config()


############################
# ExportConfig
############################


@router.get("/export", response_model=dict)
async def export_config(user=Depends(get_admin_user)):
    return get_config()


class SetDefaultModelsForm(BaseModel):
    models: str


class PromptSuggestion(BaseModel):
    title: list[str]
    content: str


class SetDefaultSuggestionsForm(BaseModel):
    suggestions: list[PromptSuggestion]


############################
# SetDefaultModels
############################


@router.post("/default/models", response_model=str)
async def set_global_default_models(
    request: Request, form_data: SetDefaultModelsForm, user=Depends(get_admin_user)
):
    request.app.state.config.DEFAULT_MODELS = form_data.models
    return request.app.state.config.DEFAULT_MODELS


@router.post("/default/suggestions", response_model=list[PromptSuggestion])
async def set_global_default_suggestions(
    request: Request,
    form_data: SetDefaultSuggestionsForm,
    user=Depends(get_admin_user),
):
    data = form_data.model_dump()
    request.app.state.config.DEFAULT_PROMPT_SUGGESTIONS = data["suggestions"]
    return request.app.state.config.DEFAULT_PROMPT_SUGGESTIONS


############################
# SetBanners
############################


class SetBannersForm(BaseModel):
    banners: list[BannerModel]


@router.post("/banners", response_model=list[BannerModel])
async def set_banners(
    request: Request,
    form_data: SetBannersForm,
    user=Depends(get_admin_user),
):
    data = form_data.model_dump()
    request.app.state.config.BANNERS = data["banners"]
    return request.app.state.config.BANNERS


@router.get("/banners", response_model=list[BannerModel])
async def get_banners(
    request: Request,
    user=Depends(get_verified_user),
):
    return request.app.state.config.BANNERS


############################
# Chat Profiles
############################

class KnowledgeBaseInfo(BaseModel):
    id: str
    label: str
   
class KnowledgeBaseForm(KnowledgeBaseInfo):
    desc: str
    # embedding_model: str
    # type: general or scrape websites
    used_by_profiles: list[str] = []
    docs: list[object] = []

class ChatProfileForm(BaseModel):
    label: str
    id: str
    roles_allowed: list[str] = ['all']
    enabled: bool
    params: dict
    knowledge_bases: list[KnowledgeBaseInfo] = [] 

@router.get("/chat/profiles/all")
async def get_all_chat_profiles(
    request: Request,
    user=Depends(get_verified_user),
):
    return request.app.state.config.CHAT_PROFILES

@router.get("/chat/profiles/filtered")
async def get_filtered_chat_profiles(
    request: Request,
    user=Depends(get_verified_user),
):
    all_profiles = request.app.state.config.CHAT_PROFILES
    filtered_profiles = [p for i, p in enumerate(all_profiles) if p["enabled"]]
    
    if user.role != "admin":
        filtered_profiles = [p for i, p in enumerate(filtered_profiles) if user.role in p["roles_allowed"]]

    return filtered_profiles

@router.get("/chat/profile/{profile_id}")
async def get_chat_profile_by_id(
    request: Request,
    profile_id: str,
    user=Depends(get_admin_user),
):
    profile = next((p for p in request.app.state.config.CHAT_PROFILES if p["id"] == profile_id), None)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    return profile

@router.post("/chat/profile/add")
async def add_chat_profile(
    request: Request,
    form_data: ChatProfileForm,
    user=Depends(get_admin_user),
):
    id = str(uuid.uuid4())

    chat_profiles = request.app.state.config.CHAT_PROFILES

    profile = {
        **form_data.model_dump(),
        "id": id
    }

    chat_profiles.append(profile)

    request.app.state.config.CHAT_PROFILES = chat_profiles

    return {
        "profile_id": id
    }

@router.post("/chat/profile/update")
async def update_chat_profile(
    request: Request,
    form_data: ChatProfileForm,
    user=Depends(get_admin_user)
):
    if form_data.id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile id is required",
        )
    
    all_profiles = request.app.state.config.CHAT_PROFILES

    for idx, profile in enumerate(all_profiles):
        if profile["id"] == form_data.id:
            existing_kb_ids = {kb["id"] for kb in profile["knowledge_bases"]}
            new_kb_ids = {kb.id for kb in form_data.knowledge_bases}

            removed_kb_ids = existing_kb_ids - new_kb_ids
            added_kb_ids = new_kb_ids - existing_kb_ids

            all_knowledge_bases = request.app.state.config.KNOWLEDGE_BASES

            # Remove profile id from knowledge bases that are no longer used
            for removed_kb_id in removed_kb_ids:
                result = next(((idx, _kb) for idx, _kb in enumerate(all_knowledge_bases) if _kb["id"] == removed_kb_id), None)

                if result is None:
                    # raise HTTPException(
                    #     status_code=status.HTTP_404_NOT_FOUND,
                    #     detail=f"Knowledge base {added_kb_id.label} not found",
                    # )
                    print(f"Knowledge base {removed_kb_id} not found")

                index = result[0]
                kb = result[1]
                
                if form_data.id in kb["used_by_profiles"]:
                    kb["used_by_profiles"] = [pid for pid in kb["used_by_profiles"] if pid != form_data.id]
                    all_knowledge_bases[index] = kb

            for added_kb_id in added_kb_ids:
                result = next(((idx, _kb) for idx, _kb in enumerate(all_knowledge_bases) if _kb["id"] == added_kb_id), None)

                if result is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Knowledge base {added_kb_id.label} not found",
                    )

                index = result[0]
                kb = result[1]

                if form_data.id not in kb["used_by_profiles"]:
                    kb["used_by_profiles"].append(form_data.id)
                    all_knowledge_bases[index] = kb

            request.app.state.config.KNOWLEDGE_BASES = all_knowledge_bases

            all_profiles[idx] = {
                **form_data.model_dump()
            }

            request.app.state.config.CHAT_PROFILES = all_profiles

            return {
                "profile": request.app.state.config.CHAT_PROFILES[idx]
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Profile not found",
    )
    

@router.delete("/chat/profile/{profile_id}")  
async def delete_chat_profile(
    profile_id: str,
    request: Request,
    user=Depends(get_admin_user),
):
    chat_profiles = request.app.state.config.CHAT_PROFILES

    profile = next((p for p in chat_profiles if p["id"] == profile_id), None)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    request.app.state.config.CHAT_PROFILES = [p for p in chat_profiles if p["id"] != profile_id]

    knowledge_bases_attached = profile["knowledge_bases"]

    knowledge_bases = request.app.state.config.KNOWLEDGE_BASES

    for kba in knowledge_bases_attached:
        result = next(((idx, _kb) for idx, _kb in enumerate(knowledge_bases) if _kb["id"] == kba["id"]), None)
        if result is not None:
            index = result[0]
            kb = result[1]
            kb["used_by_profiles"] = [pid for pid in kb["used_by_profiles"] if pid != profile_id]
            knowledge_bases[index] = kb

    request.app.state.config.KNOWLEDGE_BASES = knowledge_bases

    return {
        "id": profile_id
    }

############################
# Knowledge Bases
############################

@router.get("/knowledge-bases")
async def get_knowledge_bases(
    request: Request,
    user=Depends(get_admin_user),
):
    # TODO: only return basic info
    return request.app.state.config.KNOWLEDGE_BASES

@router.get("/knowledge-base/{kb_id}")
async def get_knowledge_base_by_id(
    request: Request,
    kb_id: str,
    user=Depends(get_admin_user),
):
    kb = next((_kb for _kb in request.app.state.config.KNOWLEDGE_BASES if _kb["id"] == kb_id), None)

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    
    return kb

@router.post("/knowledge-base/add")
async def add_knowledge_base(
    request: Request,
    form_data: KnowledgeBaseForm,
    user=Depends(get_admin_user),
):
    id = str(uuid.uuid4())

    knowledge_bases = request.app.state.config.KNOWLEDGE_BASES

    knowledge_base = {
        **form_data.model_dump(),
        "id": id
    }

    knowledge_bases.append(knowledge_base)

    request.app.state.config.KNOWLEDGE_BASES = knowledge_bases

    return {
        "kb_id": id
    }

@router.post("/knowledge-base/update")
async def update_knowledge_base(
    request: Request,
    form_data: KnowledgeBaseForm,
    user=Depends(get_admin_user)
):
    if form_data.id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knowledge base id is required",
        )
    
    for idx, kb in enumerate(request.app.state.config.KNOWLEDGE_BASES):
        if kb["id"] == form_data.id:
            request.app.state.config.KNOWLEDGE_BASES[idx] = {
                **form_data.model_dump()
            }
            return {
                "kb": request.app.state.config.KNOWLEDGE_BASES[idx]
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Knowledge base not found",
    )

@router.delete("/knowledge-base/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    request: Request,
    user=Depends(get_admin_user),
):
    if kb_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Knowledge base id is required",
        )
    
    knowledge_bases = request.app.state.config.KNOWLEDGE_BASES

    kb = next((_kb for _kb in knowledge_bases if _kb["id"] == kb_id), None)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    
    chat_profiles = request.app.state.config.CHAT_PROFILES
    for pid in kb["used_by_profiles"]:
        result = next(((idx, p) for idx, p in enumerate(chat_profiles) if p["id"] == pid), None)
        if result is not None:
            index = result[0]
            profile = result[1]
            profile["knowledge_bases"] = [kb for kb in profile["knowledge_bases"] if kb["id"] != kb_id]
            chat_profiles[index] = profile
    
    request.app.state.config.CHAT_PROFILES = chat_profiles

    request.app.state.config.KNOWLEDGE_BASES = [kb for kb in knowledge_bases if kb["id"] != kb_id]

    return {
        "id": kb_id
    }

# TODO: remove
# clear all knowledge bases
@router.delete("/knowledge-bases")
async def delete_all_knowledge_bases(
    request: Request,
    user=Depends(get_admin_user),
):
    request.app.state.config.KNOWLEDGE_BASES = []
    return {
        "status": "success"
    }