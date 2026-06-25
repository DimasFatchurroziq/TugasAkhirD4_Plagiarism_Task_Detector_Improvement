# # api/routes.py
# from fastapi import APIRouter, UploadFile, File, Depends
# from src.api.v1.dependencies import get_job_service

# hash_router = APIRouter()

# @hash_router.get("/hashes/{doc_id}")
# async def get_bb(doc_id: str, service = Depends(get_job_service)):
#     return await service.get_bb(doc_id)