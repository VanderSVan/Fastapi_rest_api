from dataclasses import dataclass


@dataclass
class JSONException(Exception):
    status_code: int
    message: str
