from dataclasses import asdict

from fastapi import Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from src.models.user import UserModel
from src.models.schedule import ScheduleModel
from src.crud_operations.schedule import ScheduleOperation
from src.swagger.schedule import (
    ScheduleInterfaceGetAll,
    ScheduleInterfaceDelete,
    ScheduleInterfacePatch,
    ScheduleInterfacePost,

    ScheduleOutputGetAll,
    ScheduleOutputGet,
    ScheduleOutputDelete,
    ScheduleOutputPatch,
    ScheduleOutputPost
)
from src.schemes.schedule.base_schemes import ScheduleGetSchema

from src.utils.dependencies.db import get_db
from src.utils.dependencies.auth import get_current_confirmed_user
from src.utils.responses.main import get_text

# Unfortunately attribute 'prefix' in InferringRouter does not work correctly (duplicate prefix).
# So I have a prefix in each function.
router = InferringRouter(tags=['schedule'])


@cbv(router)
class Schedule:
    db: Session = Depends(get_db)
    user: UserModel = Depends(get_current_confirmed_user)

    def __init__(self):
        self.schedule_operation = ScheduleOperation(db=self.db, user=self.user)

    @router.get("/schedules/", **asdict(ScheduleOutputGetAll()))
    def get_all_schedules(self,
                          schedule: ScheduleInterfaceGetAll = Depends(ScheduleInterfaceGetAll)
                          ) -> list[ScheduleModel] | list[None]:
        """
        Returns all schedules from db by parameters.
        Available to all confirmed users.
        """
        params: dict = dict(
            day=schedule.day,
            open_time=schedule.open_time,
            close_time=schedule.close_time,
            break_start_time=schedule.break_start_time,
            break_end_time=schedule.break_end_time
        )
        return self.schedule_operation.find_all_by_params(**params)

    @router.get("/schedules/{schedule_id}", **asdict(ScheduleOutputGet()))
    def get_schedule(self, schedule_id: int = Path(..., ge=1)) -> ScheduleGetSchema:
        """
        Returns one schedule from db by schedule id.
        Available to all confirmed users.
        """
        return self.schedule_operation.find_by_id_or_404(schedule_id)

    @router.delete("/schedules/{schedule_id}", **asdict(ScheduleOutputDelete()))
    def delete_schedule(self,
                        schedule: ScheduleInterfaceDelete = Depends(ScheduleInterfaceDelete)
                        ) -> JSONResponse:
        """
        Deletes schedule from db by schedule id.
        Only available to admins.
        """
        self.schedule_operation.delete_obj(schedule.schedule_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('delete').format(
                self.schedule_operation.model_name, schedule.schedule_id)}
        )

    @router.patch("/schedules/{schedule_id}", **asdict(ScheduleOutputPatch()))
    def patch_schedule(self,
                       schedule: ScheduleInterfacePatch = Depends(ScheduleInterfacePatch)
                       ) -> JSONResponse:
        """
        Updates schedule data.
        Only available to admins.
        """
        self.schedule_operation.update_obj(schedule.schedule_id, schedule.data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": get_text('patch').format(
                self.schedule_operation.model_name, schedule.schedule_id)}
        )

    @router.post("/schedules/create", **asdict(ScheduleOutputPost()))
    def add_schedule(self,
                     schedule: ScheduleInterfacePost = Depends(ScheduleInterfacePost),
                     ) -> JSONResponse:
        """
        Adds new schedule into db.
        Only available to admins.
        """
        schedule = self.schedule_operation.add_obj(schedule.data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": get_text('post').format(
                self.schedule_operation.model_name, schedule.id)}
        )
