import json

import aiohttp
import asyncio
import async_timeout

from lambda_decorators import (
    async_handler, load_json_body, json_http_resp, no_retry_on_failure, cors_headers)


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.json()

@async_handler
async def async_example():
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            fetch(session, 'http://httpbin.org/delay/3'),
            fetch(session, 'http://httpbin.org/delay/3'),
            fetch(session, 'http://httpbin.org/delay/3'),
            fetch(session, 'http://httpbin.org/delay/3'),
        )


@load_json_body
def get_foo(event, context):
    return {'body': event['body'].get('foo')}


@json_http_resp
def hello(event, context):
    return {'hello': 'world'}


@no_retry_on_failure
def schedule_test(event, context):
    raise Exception


@cors_headers('https://example.com')
@json_http_resp
def cors_customized(event, context):
    return {}


@cors_headers(origin='https://example.com', credentials=True)
@json_http_resp
def cors_customized2(event, context):
    return {}

@cors_headers
@json_http_resp
def cors_default(event, context):
    return {}
