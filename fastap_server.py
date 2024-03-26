#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:23:51 2024

@author: Luraminaki
"""

#===================================================================================================
import sys
import uuid
import time
import json
import inspect

from pathlib import Path

import logging
import datetime

import asyncio
import fastapi

#pylint: disable=wrong-import-position, wrong-import-order

#pylint: enable=wrong-import-position, wrong-import-order
#===================================================================================================

__version__ = '0.1.0'


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(formatter)
logger = logging.getLogger("Fast_Server")
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


conf_file = Path("config.json").expanduser()
with conf_file.open('r', encoding='utf-8') as f:
    conf: dict = json.load(f)


class Slow_Process ():
    def __init__(self) -> None:
        self.uuid = str(uuid.uuid4())
        self.config = conf


    def wait(self):
        curr_func = inspect.currentframe().f_code.co_name

        now = str(datetime.datetime.now())

        time.sleep(conf.get('waiting_time', 5))
        time.sleep(conf.get('waiting_time', 5))

        return { "name": curr_func, "response_start": now, "response_end": str(datetime.datetime.now()), "from": self.uuid }

    async def wait_faster(self):
        curr_func = inspect.currentframe().f_code.co_name

        now = str(datetime.datetime.now())

        task1 = asyncio.create_task(asyncio.sleep(conf.get('waiting_time', 5)))
        task2 = asyncio.create_task(asyncio.sleep(conf.get('waiting_time', 5)))

        await task1
        await task2

        return { "name": curr_func, "response_start": now, "response_end": str(datetime.datetime.now()), "from": self.uuid }


app = fastapi.FastAPI()

@app.get("/sync")
def test_sync() -> dict:
    curr_func = inspect.currentframe().f_code.co_name

    gotta_go_fast = Slow_Process()
    logger.info("%s -- START at: %s for session: %s", curr_func, str(datetime.datetime.now()), str(gotta_go_fast.uuid).split("-", maxsplit=1)[0])

    result = gotta_go_fast.wait()

    return result


@app.get("/async")
async def test_async() -> dict:
    curr_func = inspect.currentframe().f_code.co_name

    gotta_go_fast = Slow_Process()
    logger.info("%s -- START at: %s for session: %s", curr_func, str(datetime.datetime.now()), str(gotta_go_fast.uuid).split("-", maxsplit=1)[0])

    result = await gotta_go_fast.wait_faster()

    return result

# gunicorn fastap_server:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
