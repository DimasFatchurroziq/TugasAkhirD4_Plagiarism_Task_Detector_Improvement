from repositories.file_repository import FileRepository
from repositories.hash_repository import HashRepository
from repositories.gst_repository import GstRepository
from repositories.similarity_repository import SimilarityRepository

from services.preprocessing_service import PreprocessingService
from services.rollinghash_service import RollingHashService
from services.winnowing_service import WinnowingService
from services.matching_service import MatchingService
from services.gst_service import GstService
from services.similarity_service import SimilarityService

def get_preprocess_service():
    repository = FileRepository()
    return PreprocessingService(repository)

def get_rollinghash_service():
    repository = HashRepository()
    return RollingHashService(repository)

def get_fingerprint_service():
    return WinnowingService()

def get_matching_service():
    return MatchingService()

def get_gst_service():
    repository = GstRepository()
    return GstService(repository)

def get_similarity_service():
    repository = SimilarityRepository()
    return SimilarityService(repository)