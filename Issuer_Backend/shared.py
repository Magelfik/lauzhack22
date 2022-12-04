from typing import List

from expiring_dict import ExpiringDict

NULL_UUID: str = "00000000000000000000000000000000"
IDENTITY_CREDENTIAL_ID: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63828:e-id"
INSURANCE_CREDENTIAL_ID: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63887:OPM insurance"
DEFAULT_PAUSE_TIME: float = 0.1
DEFAULT_TIMEOUT: int = int(600/DEFAULT_PAUSE_TIME)  # timeout : ~600s ~ 10min
DEFAULT_INSURANCE_ID = 0

cache = ExpiringDict(600)

