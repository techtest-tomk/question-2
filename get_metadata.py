import aiohttp
import asyncio
import sys
import json

URL = 'http://localhost:1338/latest/meta-data/'


async def split_items_from_response(response):
    value = await response.text()
    return value.split('\n')


async def get_item(session, url, items):
    dicts = {}
    list = []

    for item in items:
        if item:
            async with session.get(url+item) as resp:
                status = resp.status
                if status != 200:
                    if len(items) == 1:
                        return item
                    list.append(item)
                    continue

                if 'application/json' in resp.headers["Content-Type"]:
                    value = await resp.json()
                    dicts[item.replace('/', '')] = value
                    continue

                vals = await split_items_from_response(resp)
                dicts[item.replace('/', '')] = await get_item(session, url + item, vals)

    if not list:
        return dicts
    if dicts:
        list.append(dicts)
    return list


async def get_items(path):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL+path) as resp:
            if resp.status != 200:
                raise AttributeError(f'{path} not found')
            items = await split_items_from_response(resp)
            return json.dumps(await get_item(session, URL + path, items))


def get_user_path():
    if len(sys.argv) < 2:
        return ''
    path = sys.argv[1]
    if path[-1] != '/':
        path += '/'

    return path


path = get_user_path()

json = asyncio.run(get_items(path))

print(json)
