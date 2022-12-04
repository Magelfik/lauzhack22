from typing import List

from expiring_dict import ExpiringDict

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63828:e-id"
DEFAULT_PAUSE_TIME: float = 0.1
DEFAULT_TIMEOUT: int = int(600/DEFAULT_PAUSE_TIME)  # timeout : ~600s ~ 10min

cache = ExpiringDict(600)

