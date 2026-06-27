# api/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db


from src.repositories.job_repository import JobRepository
from src.repositories.document_repository import DocumentRepository
from src.repositories.block_repository import BlockRepository
from src.repositories.mapping_repository import MappingRepository
from src.repositories.hash_repository import HashRepository
from src.repositories.comparison_repository import ComparisonRepository
from src.repositories.rkrgst_repository import RkrgstRepository
from src.repositories.sbert_repository import SBertRepository
from src.repositories.block_embedding_repository import BlockEmbeddingRepository


from src.services.job_service import JobService
from src.services.document_service import DocumentService
from src.services.comparison_service import ComparisonService
from src.services.sbert_service import SBertService
from src.services.rkrgst_service import RkrgstService
from src.services.process_service import ProcessService
from src.services.convert_service import ConvertService


from src.services.process.tahap_1 import Tahap_1
from src.services.process.tahap_2 import Tahap_2
from src.services.process.tahap_3 import Tahap_3
from src.services.process.tahap_4 import Tahap_4
from src.services.process.tahap_5 import Tahap_5
from src.services.process.tahap_6 import Tahap_6
from src.services.process.tahap_7 import Tahap_7

from src.services.convert.tahap_8 import Tahap_8
from src.services.convert.tahap_9 import Tahap_9
from src.services.convert.tahap_10 import Tahap_10


# from sentence_transformers import SentenceTransformer
# MODEL_NAME = "firqaaa/indo-sentence-bert-base"
# sbert_model_instance = SentenceTransformer(MODEL_NAME)
import os
from sentence_transformers import SentenceTransformer
MODEL = os.getenv("SBERT_MODEL_PATH", "firqaaa/indo-sentence-bert-base")
sbert_model_instance = SentenceTransformer(MODEL)


async def db_session(db: AsyncSession = Depends(get_db)):
    return db

def get_job_repo(db: AsyncSession = Depends(db_session)):
    return JobRepository(db)

def get_doc_repo(db: AsyncSession = Depends(db_session)):
    return DocumentRepository(db)

def get_block_repo(db: AsyncSession = Depends(db_session)):
    return BlockRepository(db)

def get_map_repo(db: AsyncSession = Depends(db_session)):
    return MappingRepository(db)

def get_hash_repo(db: AsyncSession = Depends(db_session)):
    return HashRepository(db)

def get_compare_repo(db: AsyncSession = Depends(db_session)):
    return ComparisonRepository(db)

def get_rkrgst_repo(db: AsyncSession = Depends(db_session)):
    return RkrgstRepository(db)

def get_sbert_repo(db: AsyncSession = Depends(db_session)):
    return SBertRepository(db)

def get_block_embed_repo(db: AsyncSession = Depends(db_session)):
    return BlockEmbeddingRepository(db)


##################################################################


def get_tahap1_service():
    return Tahap_1()

def get_tahap2_service():
    return Tahap_2()

def get_tahap3_service():
    return Tahap_3()

def get_tahap4_service():
    return Tahap_4()

def get_tahap5_service():
    return Tahap_5()

def get_tahap6_service():
    return Tahap_6()

def get_tahap7_service():
    return Tahap_7()

def get_tahap8_service():
    return Tahap_8()

def get_tahap9_service():
    return Tahap_9()

def get_tahap10_service():
    return Tahap_10()


##################################################################



def get_job_service(
    job_repo: JobRepository = Depends(get_job_repo),
):
    return JobService(job_repo)

def get_doc_service(
    job_serv: JobService = Depends(get_job_service),

    doc_repo: DocumentRepository = Depends(get_doc_repo),
):
    return DocumentService(job_serv, doc_repo)

def get_compare_service(
    job_serv: JobService = Depends(get_job_service),
    doc_serv: DocumentService = Depends(get_doc_service),

    compare_repo: ComparisonRepository = Depends(get_compare_repo),
):
    return ComparisonService(job_serv, doc_serv, compare_repo)

def get_sbert_service(
    sbert_repo: SBertRepository = Depends(get_sbert_repo),
):
    return SBertService(sbert_repo)

def get_rkrgst_service(
    rkrgst_repo: RkrgstRepository = Depends(get_rkrgst_repo),
):
    return RkrgstService(rkrgst_repo)









def get_process_service(
    compare_serv: ComparisonService = Depends(get_compare_service),
    rkrgst_serv: RkrgstService = Depends(get_rkrgst_service),

    tahap1_serv: Tahap_1 = Depends(get_tahap1_service),
    tahap2_serv: Tahap_2 = Depends(get_tahap2_service),
    tahap3_serv: Tahap_3 = Depends(get_tahap3_service),
    tahap4_serv: Tahap_4 = Depends(get_tahap4_service),
    tahap5_serv: Tahap_5 = Depends(get_tahap5_service),
    tahap6_serv: Tahap_6 = Depends(get_tahap6_service),
    tahap7_serv: Tahap_7 = Depends(get_tahap7_service),

    job_repo: JobRepository = Depends(get_job_repo),
    doc_repo: DocumentRepository = Depends(get_doc_repo),
    block_repo: BlockRepository = Depends(get_block_repo),
    map_repo: MappingRepository = Depends(get_map_repo),
    hash_repo: HashRepository = Depends(get_hash_repo),
    compare_repo: ComparisonRepository = Depends(get_compare_repo),
    rkrgst_repo: RkrgstRepository = Depends(get_rkrgst_repo),
    sbert_repo: SBertRepository = Depends(get_sbert_repo),
    block_embed_repo: BlockEmbeddingRepository = Depends(get_block_embed_repo)
):
    return ProcessService(
        compare_serv, rkrgst_serv,
        sbert_model_instance,
        tahap1_serv, tahap2_serv, tahap3_serv, tahap4_serv, tahap5_serv, tahap6_serv, tahap7_serv,
        job_repo, doc_repo, block_repo, map_repo, hash_repo, compare_repo, rkrgst_repo, sbert_repo, block_embed_repo
        )


def get_convert_service(
    compare_serv: ComparisonService = Depends(get_compare_service),

    tahap8_serv: Tahap_8 = Depends(get_tahap8_service),
    tahap9_serv: Tahap_9 = Depends(get_tahap9_service),
    tahap10_serv: Tahap_10 = Depends(get_tahap10_service),

    block_repo: BlockRepository = Depends(get_block_repo),
    compare_repo: ComparisonRepository = Depends(get_compare_repo),
    rkrgst_repo: RkrgstRepository = Depends(get_rkrgst_repo),
):
    return ConvertService(
        compare_serv,
        tahap8_serv, tahap9_serv, tahap10_serv,
        block_repo, compare_repo, rkrgst_repo
        )
