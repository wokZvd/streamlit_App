"""
JSON Export / Import 기능
"""

import json
from typing import Dict



def export_json(
    data:Dict
)->str:

    return json.dumps(

        data,

        ensure_ascii=False,

        indent=4

    )



def import_json(
    file
)->Dict:


    content=file.read()


    if isinstance(
        content,
        bytes
    ):

        content=content.decode(
            "utf-8"
        )


    return json.loads(
        content
    )
