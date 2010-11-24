#!/usr/bin/env python
import traceback

import bottle
from bottle import route, request, static_file

from mips import Mips
from interpreter import Interpreter
   
@route("/mips", template="mips")
def mips_ui():
    return {}

@route("/mips/execute", method="POST")
def execution():
    text = request.POST.get("text")
    data_forwarding = bool(request.POST.get("data_forwarding", False))

    if text:
    
        mips = Mips(text, data_forwarding=data_forwarding)

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

@route("/mips/compile", method="POST")
def compiler():
    text = request.POST.get("text")
    
    interpreter = Interpreter(text)
    interpreter.compile()
    result = str(interpreter)
    return {'result':result}
    
@route("/static/:path#.+#")
def static_server(path):
    return static_file(path, root="./static")
    
if __name__ == "__main__":
    bottle.debug(True)
    bottle.run(reloader=True, host="0.0.0.0")
