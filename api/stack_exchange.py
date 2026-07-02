import os
from stackapi import StackAPI
from ..settings import SITE_NAME


def create_site():
    api_key = os.getenv("SE_API_KEY")
    if api_key:
        return StackAPI(SITE_NAME, key=api_key)
    return StackAPI(SITE_NAME)

SITE = create_site()
