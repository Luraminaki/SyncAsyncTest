#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:23:51 2024

@author: Luraminaki
"""

#===================================================================================================
import sys
import time
import json
import enum
import inspect

from pathlib import Path

import logging
import datetime

import asyncio
import aiohttp

#pylint: disable=wrong-import-position, wrong-import-order

#pylint: enable=wrong-import-position, wrong-import-order
#===================================================================================================

__version__ = '0.1.0'


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(formatter)
logger = logging.getLogger("Async_Clients")
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


conf_file = Path("config.json").expanduser()
with conf_file.open('r', encoding='utf-8') as f:
    conf: dict = json.load(f)


class HeaderType(enum.Enum):
    DEFAULT = 0
    NONE = 1


def set_headers(ht: HeaderType=HeaderType.DEFAULT, cookies: dict=None) -> dict:
    if cookies is None:
        cookies = {}

    if ht == HeaderType.DEFAULT:
        return {'Content-Type': 'application/json'}

    return {}


def process_response(response: str, api: str) -> dict:
    curr_func = inspect.currentframe().f_code.co_name
    resp = {}

    try:
        resp = json.loads(response)

    except Exception as error:
        logger.info("%s -- Distant ressource %s answer is not JSON -- Error: %s", curr_func, api, error)

    return resp


async def request(api_route: str, user: str=None, header: HeaderType=HeaderType.DEFAULT, cookies: dict=None) -> dict:
    curr_func = inspect.currentframe().f_code.co_name

    if cookies is None:
        cookies = {}

    if user is None:
        user = '0'

    head = set_headers(header)

    now = str(datetime.datetime.now())
    resp = {"user": user, "request_start": now}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_route, headers=head, cookies=cookies, timeout=conf.get('request_timeout', 3600)) as response:
                resp = await response.text("utf-8")
                proc_res = process_response(resp, api_route)
                proc_res.update({"user": user, "request_start": now, "request_end": str(datetime.datetime.now())})
        return proc_res

    except Exception as error:
        logger.error('%s -- Could not perform request from user %s -- Returning default response -- %s', curr_func, user, error)
        resp.update({"request_end": str(datetime.datetime.now())})
        return resp


async def main(nb_user: int, api: str) -> None:
    curr_func = inspect.currentframe().f_code.co_name

    requests_tasks = set()
    requests_throttled = []

    logger.info("%s -- Preparing %s concurrent Requests to %s", curr_func, conf.get('concurrent_user', 50), api)

    for user in range(nb_user):
        logger.debug("%s -- User n°%s/%s", curr_func, user+1, nb_user)
        logger.debug("%s -- URL %s", curr_func, api)

        task = asyncio.create_task(request(api, str(user)))
        requests_tasks.add(task)
        task.add_done_callback(requests_tasks.discard)

    if requests_tasks:
        logger.info("%s -- Waiting for the %s Requests answers", curr_func, len(requests_tasks))
        requests_outcome = await asyncio.gather(*requests_tasks)

        for resp in requests_outcome:
            request_start = datetime.datetime.strptime(resp['request_start'], '%Y-%m-%d %H:%M:%S.%f')
            request_end = datetime.datetime.strptime(resp['request_end'], '%Y-%m-%d %H:%M:%S.%f')
            request_delta = request_end - request_start

            rule_throttling_happenned = request_delta.seconds > (2 + 0.1)*conf.get('waiting_time', 5)

            if rule_throttling_happenned:
                requests_throttled.append(resp)

        logger.info("%s -- Requests sent: %s, Requests throttled: %s", curr_func, len(requests_outcome), len(requests_throttled))

        if requests_throttled:
            logger.info("%s -- Exemple throttled request: %s", curr_func, json.dumps(requests_throttled[0], indent=4))


if __name__ == "__main__":
    curr_func = inspect.currentframe().f_code.co_name

    tic = time.perf_counter()
    asyncio.run(main(nb_user=conf.get('concurrent_user', 50), api='http://0.0.0.0:8080/sync'))
    tac = time.perf_counter() - tic
    logger.info("%s -- ENDED in %s second(s)", curr_func, tac)
    logger.info("#=====================================================")

    tic = time.perf_counter()
    asyncio.run(main(nb_user=conf.get('concurrent_user', 50), api='http://0.0.0.0:8080/async'))
    tac = time.perf_counter() - tic
    logger.info("%s -- ENDED in %s second(s)", curr_func, tac)
    logger.info("#=====================================================")

# python3 async_clients.py
