import json
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from open_webui.utils.utils import get_admin_user, get_verified_user
from open_webui.apps.webui.models.knowledge_bases import KnowledgeBaseForm, KnowledgeBases, KnowledgeBaseFullResponse, KnowledgeBaseResponse
from open_webui.apps.webui.models.chat_profiles import ChatProfiles
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status

router = APIRouter()

############################
# Knowledge Bases
############################

@router.get("/", response_model=list[KnowledgeBaseFullResponse])
async def get_knowledge_bases(
    request: Request,
    user=Depends(get_admin_user),
):
    kbs = KnowledgeBases.get_all_knowledge_bases()

    return [KnowledgeBaseFullResponse(
        **{
            **kb.model_dump(),
            "documents": json.loads(kb.documents),
        }
    ) for kb in kbs]

@router.get("/info", response_model=list[KnowledgeBaseResponse])
async def get_knowledge_bases_info(
    request: Request,
    user=Depends(get_admin_user),
):
    kbs = KnowledgeBases.get_all_knowledge_bases()

    return [KnowledgeBaseResponse(**kb.model_dump()) for kb in kbs]

@router.get("/{kb_id}", response_model=KnowledgeBaseFullResponse)
async def get_knowledge_base_by_id(
    request: Request,
    kb_id: str,
    user=Depends(get_admin_user),
):
    kb = KnowledgeBases.get_knowledge_base_by_id(kb_id)

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    
    return KnowledgeBaseFullResponse(
        **{
            **kb.model_dump(),
            "documents": json.loads(kb.documents),
        }
    )

@router.post("/add")
async def add_knowledge_base(
    request: Request,
    form_data: KnowledgeBaseForm,
    user=Depends(get_admin_user),
):
    kb = KnowledgeBases.insert_new_knowledge_base(form_data, user.id)

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add knowledge base",
        )

    return {
        "kb_id": kb.id
    }

@router.post("/update/{kb_id}", response_model=KnowledgeBaseFullResponse)
async def update_knowledge_base(
    request: Request,
    kb_id: str,
    form_data: KnowledgeBaseForm,
    user=Depends(get_admin_user)
):
    kb = KnowledgeBases.update_knowledge_base_by_id(kb_id, form_data)

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    
    return KnowledgeBaseFullResponse(
        **{
            **kb.model_dump(),
            "documents": json.loads(kb.documents),
        }
    )

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    request: Request,
    user=Depends(get_admin_user),
):
    result = KnowledgeBases.delete_knowledge_base_by_id(kb_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found",
        )
    
    result = ChatProfiles.remove_kb_from_chat_profiles(kb_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found in chat profiles",
        )

    return {
        "id": kb_id
    }