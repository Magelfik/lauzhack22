import uuid

from shared import DEFAULT_INSURANCE_ID


class InvalidClaimsException(Exception):
    pass


def forge(claims: dict) -> dict:
    if "first name" not in claims or "last name" not in claims or "birth" not in claims:
        print(claims)
        raise InvalidClaimsException()

    attributes: dict = dict(claims.items())
    attributes["insurance id"] = DEFAULT_INSURANCE_ID
    attributes["uid"] = uuid.uuid1().hex

    return attributes

