import argparse
import os
import pathlib
import socket
import sys

sys.path.append('./lib')

from aiohttp import web

import src


def init_app(lpatch=str(pathlib.Path().absolute()) + '/'):
    new_handler = src.ApiHandler(lpatch)
    new_app = web.Application()
    with new_handler.log.catch('Error routing configure', onerror=lambda _: sys.exit(1)):
        if new_handler.parms.get('GET_STATUS_ENABLED', False):
            new_app.add_routes([web.get(new_handler.apiurl + '/status', new_handler.get_stat)])
        else:
            del new_handler.swagger_descriptions['paths'][new_handler.apiurl + '/status']
            del new_handler.swagger_descriptions['components']['schemas']['status_out']

        if new_handler.parms.get('GET_ENABLED', False):
            new_app.add_routes([web.get(new_handler.apiurl + '/{message_idt}/{source_system}', new_handler.get_record)])
        else:
            del new_handler.swagger_descriptions['paths'][new_handler.apiurl + '/{message_idt}/{source_system}']['get']
            del new_handler.swagger_descriptions['components']['schemas']['get_required_out']

        if new_handler.parms.get('POST_ENABLED', False):
            new_app.add_routes(
                [web.post(new_handler.apiurl + '/{message_idt}/{source_system}', new_handler.post_record)])
        else:
            del new_handler.swagger_descriptions['paths'][new_handler.apiurl + '/{message_idt}/{source_system}']['post']
            del new_handler.swagger_descriptions['components']['schemas']['post_required_out']
        if new_handler.swaggerEnabled:
            from aiohttp_swagger import setup_swagger

            setup_swagger(new_app, swagger_url=new_handler.swagger_url, swagger_info=new_handler.swagger_descriptions,
                          ui_version=3)

    new_handler.log.info(
        'Start process worker at URL = <host>:<port>%s , template version: %s , configurations release %s' %
        (new_handler.apiurl, new_handler.version, new_handler.release))

    return new_app, new_handler


def get_sock(socket_path):
    if socket_path is None:
        return None
    if len(socket_path) < 1:
        return None
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    if os.path.exists(socket_path):
        os.unlink(socket_path)
    s.bind(socket_path)
    os.chmod(socket_path, 0o660)
    return s


if __name__ == "__main__":
    app, handler = init_app()
    parser = argparse.ArgumentParser(description="aiohttp server")
    parser.add_argument('--path')
    parser.add_argument('--port')
    args = parser.parse_args()
    with handler.log.catch(message='Error create socket', onerror=lambda _: sys.exit(1)):
        serv_sock = get_sock(args.path)
    try:
        if handler.ACCESS_LOG:
            web.run_app(app, access_log=handler.log, sock=serv_sock, port=args.port)
        else:
            web.run_app(app, access_log=None, sock=serv_sock, port=args.port)
    finally:
        handler.db_disconnect()
        handler.log.info('Server stopped')
        handler.log.complete()
