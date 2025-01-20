import sys
from urllib.parse import unquote_plus

from .tsdir import TSDir


def api(tsdir: TSDir='.', *tokens):
    try:
        from flask import Flask, make_response, request
    except ImportError:
        print("'api' requires 'flask' to be installed. "
              "Consider 'pip install flask'", file=sys.stderr)
        return

    if not isinstance(tsdir, TSDir):
        tsdir = TSDir(str(tsdir))

    app = Flask('Delta')

    @app.route("/")
    @app.route('/<path:sub_path>')
    def return_items(sub_path=''):
        if tokens:
            if request.args.get('token') not in tokens:
                return make_response('Unauthorized token', 401)

        tbl = tsdir(unquote_plus(sub_path))

        item = request.args.get('item', request.args.get('date'))
        if item is not None:
            if item.startswith('-'):
                item = -int(item[1:])
            elif item.isdigit():
                item = int(item)
            else:
                item = unquote_plus(item)
            return tbl[item]

        start = request.args.get('start')
        stop = request.args.get('stop', request.args.get('end'))
        step = request.args.get('step')

        start = unquote_plus(start) if start else start
        stop = unquote_plus(stop) if stop else stop
        step = unquote_plus(step) if step else step
        return tbl[start:stop:step]

    @app.route('/subdir')
    @app.route('/<path:sub_path>/subdir')
    @app.route('/list')
    @app.route('/<path:sub_path>/list')
    def return_subdir(sub_path=''):
        if tokens:
            if request.args.get('token') not in tokens:
                return make_response('Unauthorized token', 401)
        tbl = tsdir(unquote_plus(sub_path))
        return [s.name for s in tbl.subdir()]

    @app.route('/tree')
    @app.route('/<path:sub_path>/tree')
    def return_tree(sub_path=''):
        if tokens:
            if request.args.get('token') not in tokens:
                return make_response('Unauthorized token', 401)
        tbl = tsdir(unquote_plus(sub_path))
        s = tbl.tree(print=False, limit=request.args.get('limit', 1_000))
        response = make_response(s, 200)
        response.mimetype = "text/plain"
        return response

    return app
