from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Type, Any

from fastapi import Query, Path, Body, Depends, status

from src.api.models.user import UserModel
from src.api.schemes.schedule.base_schemes import (ScheduleGetSchema,
                                                   SchedulePatchSchema,
                                                   SchedulePostSchema)
from src.api.schemes.schedule.response_schemes import (ScheduleResponsePatchSchema,
                                                       ScheduleResponseDeleteSchema,
                                                       ScheduleResponsePostSchema)
from src.api.dependencies.auth import get_current_admin_or_superuser


@dataclass
class ScheduleInterfaceGetAll:
    day: str | date = Query(default=None, description="Weekday or date")
    open_time: time = Query(default=None, description="HH:MM, More or equal", example='08:00')
    close_time: time = Query(default=None, description="HH:MM, Less or equal", example='20:00')
    break_start_time: time = Query(default=None, description="HH:MM, More or equal")
    break_end_time: time = Query(default=None, description="HH:MM, Less or equal")


@dataclass
class ScheduleInterfaceDelete:
    schedule_id: int = Path(..., ge=1)
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class ScheduleInterfacePatch:
    schedule_id: int = Path(..., ge=1)
    data: SchedulePatchSchema = Body(..., example={
        "day": "Monday",
        "open_time": "08:00",
        "close_time": "22:00",
        "break_start_time": "13:00",
        "break_end_time": "14:00"
    })
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class ScheduleInterfacePost:
    data: SchedulePostSchema = Body(..., example={
        "day": "2022-12-25",
        "open_time": "10:00",
        "close_time": "23:00",
        "break_start_time": "14:00",
        "break_end_time": "15:00"
    })
    admin: UserModel = Depends(get_current_admin_or_superuser)


@dataclass
class ScheduleOutputGetAll:
    summary: Optional[str] = 'Get all schedules by parameters'
    description: Optional[str] = (
        "**Returns** all schedules from db by **parameters**. <br />"
        "Available to all **confirmed users.**"
    )
    response_model: Optional[Type[Any]] = list[ScheduleGetSchema]
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'List of schedules'


@dataclass
class ScheduleOutputGet:
    summary: Optional[str] = 'Get schedule by schedule id'
    description: Optional[str] = (
        "**Returns** schedule from db by **schedule id**. <br />"
        "Available to all **confirmed users.**"
    )
    response_model: Optional[Type[Any]] = ScheduleGetSchema
    status_code: Optional[int] = status.HTTP_200_OK
    response_description: str = 'Schedule data'


@dataclass
class ScheduleOutputDelete:
    summary: Optional[str] = 'Delete schedule by schedule id'
    description: Optional[str] = (
        "**Deletes** schedule from db by **schedule id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = ScheduleResponseDeleteSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class ScheduleOutputPatch:
    summary: Optional[str] = 'Delete schedule by schedule id'
    description: Optional[str] = (
        "**Updates** schedule from db by **schedule id**. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = ScheduleResponsePatchSchema
    status_code: Optional[int] = status.HTTP_200_OK


@dataclass
class ScheduleOutputPost:
    summary: Optional[str] = 'Delete schedule by schedule id'
    description: Optional[str] = (
        "**Adds** new schedule into db. <br />"
        "Only available to **superuser.**"
    )
    response_model: Optional[Type[Any]] = ScheduleResponsePostSchema
    status_code: Optional[int] = status.HTTP_201_CREATED
