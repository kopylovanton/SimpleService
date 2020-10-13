import pytest
from aiohttp import web
import sys
sys.path.append('./src/python/')
from start_server import init_app
import pathlib

# def cli(loop, aiohttp_client):
#     app = web.Application()
#     app.router.add_get('/', previous)
#     app.router.add_post('/', previous)
#     return loop.run_until_complete(aiohttp_client(app))

@pytest.fixture()
def client(loop,aiohttp_client):
    app, handler = init_app(lpatch=str(pathlib.Path().absolute()) + '/src/tests/app_config/')
    return loop.run_until_complete(aiohttp_client(app)), handler