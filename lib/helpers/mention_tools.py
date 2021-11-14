from re import fullmatch


def get_id_from_mention(mention: str) -> int:
    """Given a string mention, get the id of the associated user"""
    return int(mention[3: len(mention)-1])


def verify_mention(mention: str) -> bool:
    """Given a string verify if the string is a valid mention"""
    return fullmatch("<@!\d{18}>", mention) is not None
