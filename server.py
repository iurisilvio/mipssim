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
    data_forwarding = bool(int(request.POST.get("data_forwarding", 0)))

    if text:
        mips = Mips(text, data_forwarding=data_forwarding)
        mips.run()
        return {"text":text, "result":mips.history}
        
    return {"error":"INVALID_TEXT"}

@route("/mips/compare", method="POST")
def execution():
    text = request.POST.get("text")

    if text:
        slower_mips = Mips(text, data_forwarding=False)
        slower_mips.run()
        slower_mips_state = slower_mips.current_state()

        faster_mips = Mips(text, data_forwarding=True)
        faster_mips.run()
        faster_mips_state = faster_mips.current_state()

        return {"text":text,
                "slower_mips":{"clocks":slower_mips_state["clock"],
                               "throughput":slower_mips_state["throughput"]},
                "faster_mips":{"clocks":faster_mips_state["clock"],
                               "throughput":faster_mips_state["throughput"]}}

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
