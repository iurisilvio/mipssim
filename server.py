import bottle
from bottle import route, request, static_file

from mips import Mips

@route("/mips/execute", method="POST")
def execution():
    text = request.POST.get("text")
    if text:
        mips = Mips(text)

        try:
            mips.run()
            return {"text":text, "result":mips.history}
        except:
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
    bottle.run(reloader=True)
