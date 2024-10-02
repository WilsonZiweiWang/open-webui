import json
import logging
from fastapi import APIRouter, Depends, Request
from open_webui.utils.utils import get_admin_user, get_verified_user

from fastapi import APIRouter, Depends, HTTPException, Request, status
from open_webui.apps.webui.models.chat_profiles import ChatProfileForm, ChatProfileModel, ChatProfiles, ChatProfileFullResponse, ChatProfileResponse
from open_webui.apps.webui.models.knowledge_bases import KnowledgeBases

from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()

############################
# Chat Profiles
############################

@router.get("/", response_model=list[ChatProfileFullResponse])
async def get_all_chat_profiles(
    request: Request,
    user=Depends(get_admin_user),
):
    all_profiles = ChatProfiles.get_all_chat_profiles()

    return serialize_profiles(all_profiles)

@router.get("/info", response_model=list[ChatProfileResponse])
async def get_all_chat_profiles_info(
    request: Request,
    user=Depends(get_admin_user),
):
    all_profiles = ChatProfiles.get_all_chat_profiles()

    return [ChatProfileResponse(**profile.model_dump()) for profile in all_profiles]

@router.get("/filtered", response_model=list[ChatProfileFullResponse])
async def get_filtered_chat_profiles(
    request: Request,
    user=Depends(get_verified_user),
):
    if user.role == "admin":
        all_profiles = ChatProfiles.get_all_enabled_chat_profiles()
        return serialize_profiles(all_profiles)
    
    filtered_profiles = ChatProfiles.get_filtered_enabled_chat_profiles_by_role(user.role)

    return serialize_profiles(filtered_profiles)

@router.get("/{profile_id}", response_model=ChatProfileFullResponse)
async def get_chat_profile_by_id(
    request: Request,
    profile_id: str,
    user=Depends(get_admin_user),
):
    profile = ChatProfiles.get_chat_profile_by_id(profile_id)    

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    return ChatProfileFullResponse(
                **{
                    **profile.model_dump(),
                    "roles_allowed":json.loads(profile.roles_allowed),
                    "knowledge_bases":json.loads(profile.knowledge_bases),
                    "params":json.loads(profile.params)
                }
        ) 

@router.post("/add")
async def add_chat_profile(
    request: Request,
    form_data: ChatProfileForm,
    user=Depends(get_admin_user),
):
    try:
        chat_profile = ChatProfiles.insert_new_chat_profile(user_id=user.id, form_data=ChatProfileForm(**form_data.model_dump()))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "profile_id": chat_profile.id
    }

@router.post("/update/{profile_id}", response_model=ChatProfileFullResponse)
async def update_chat_profile(
    request: Request,
    profile_id: str,
    form_data: ChatProfileForm,
    user=Depends(get_admin_user)
):
    for kb_id in form_data.knowledge_bases:
        if not KnowledgeBases.get_knowledge_base_by_id(kb_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge base not found {kb_id}",
            )
        
    chat_profile = ChatProfiles.update_chat_profile_by_id(profile_id, form_data)
    
    if chat_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    
    return ChatProfileFullResponse(
                **{
                    **chat_profile.model_dump(),
                    "roles_allowed":json.loads(chat_profile.roles_allowed),
                    "knowledge_bases":json.loads(chat_profile.knowledge_bases),
                    "params":json.loads(chat_profile.params)
                }
        )

@router.delete("/{profile_id}")  
async def delete_chat_profile(
    profile_id: str,
    request: Request,
    user=Depends(get_admin_user),
):
    result = ChatProfiles.delete_chat_profile_by_id(profile_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return {
        "id": profile_id
    }

def serialize_profiles(profiles: list[ChatProfileModel]) -> list[ChatProfileFullResponse]:
    return [ChatProfileFullResponse(
                **{
                    **profile.model_dump(),
                    "roles_allowed":json.loads(profile.roles_allowed),
                    "knowledge_bases":json.loads(profile.knowledge_bases),
                    "params":json.loads(profile.params)
                }
            ) 
            for profile in profiles]