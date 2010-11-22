TICKS = 100;
var mips = {
    _data: [],
    _current_position: null,
    _running: false,

    execute: function(text) {
        $.ajax({
            url:'/mips/execute',
            data: {"text":bytecode.value},
            success: mips._refresh,
            dataType: "json",
            type: "POST"
        });
    },

    next: function() {
        this.goto(++this._current_position);
    },
    
    prev: function() {
        this.goto(--this._current_position);
    },
    
    play: function() {
        if (this._running) {
            this.pause();
        }
        else {
            this._running = true;
            this._run();
        }
    },
    
    pause: function() {
        this._running = false;
    },
    
    _run: function() {
        if (mips._running) {
            mips.next();
            setTimeout(mips._run, TICKS);
        }
    },
    
    goto: function(position) {
        this._current_position = position;
        var state = this._data[position];
        
        var arr = ["clock", "pc", "instructions_completed"]
        for (var i=0; i < arr.length; i++) {
            var key = arr[i];
            $("#" + key).html(state[key]);
        }
        $("#throughput").html(state["throughput"].toFixed(2));
        this._set_pipeline(state["pipeline"]);
        this._set_registers(state["registers"]);
    },
    
    _refresh: function(data) {
        mips._data = data.result;
        mips.goto(0);
    },
    
    _set_registers: function(registers) {
        for (var i in registers) {
            $('#r' + i).html(registers[i]);
        }
    },
    
    _set_pipeline: function(pipeline) {
        var flags_string = function(flags) {
            var s = ""
            for (var key in flags) {
                s += key + ": " + flags[key] + "<br />"
            }
            return s;
        };
        $("#if").html(pipeline.if.text);
        $("#if_flags").html(flags_string(pipeline.if.flags));
        $("#id_").html(pipeline.id.text);
        $("#id_flags").html(flags_string(pipeline.id.flags));
        $("#ex").html(pipeline.ex.text);
        $("#ex_flags").html(flags_string(pipeline.ex.flags));
        $("#mem").html(pipeline.mem.text);
        $("#mem_flags").html(flags_string(pipeline.mem.flags));
        $("#wb").html(pipeline.wb.text);
        $("#wb_flags").html(flags_string(pipeline.wb.flags));
    },
}
