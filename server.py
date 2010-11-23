import traceback

import bottle
from bottle import route, request, static_file

from mips import Mips

@route("/mips/execute", method="POST")
def execution():
    text = request.POST.get("text")
    bypassing = bool(int(request.POST.get("bypassing", 0)))

    if text:
        mips = Mips(text)
        mips.enable_bypassing(bypassing)

        try:
            mips.run()
            return {"text":text, "result":mips.history}
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return {"error":"TIMEOUT"}
        
    return {"error":"INVALID_TEXT"}
    
@route("/mips", template="mips")
def mips_ui():
    return {}
    
@route("/static/:path#.+#")
def static_server(path):
    return static_file(path, root="./static")
    
if __name__ == "__main__":
    bottle.debug(True)
    bottle.run(reloader=True, host="0.0.0.0")
