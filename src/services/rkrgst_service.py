from src.repositories.rkrgst_repository import RkrgstRepository
from src.models.model import Rkrgst

class RkrgstService:
    def __init__(self, rkrgst_repo: RkrgstRepository):
        self.rkrgst_repo = rkrgst_repo

    async def create_rkrgst_bulk(self, comparison_id: str, rkrgst_list: list, type: str):
        rkrgst_objects = []
    
        for item in rkrgst_list:
            obj = Rkrgst(
                type=type,
                position_1_start=item[0],
                position_2_start=item[1],
                match_length=item[2],
                comparison_id=comparison_id
            )
            rkrgst_objects.append(obj)

        result = await self.rkrgst_repo.bulk_create(rkrgst_objects)

        return result
