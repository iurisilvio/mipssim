TICKS = 100;
var mips = {
    _data: [],
    _current_position: null,
    _running: false,

    execute: function(text) {
        $.ajax({
            url:'/mips/execute',
            data: {"text":text},
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
        
        if (state) {
            var arr = ["clock", "pc", "instructions_completed"]
            for (var i=0; i < arr.length; i++) {
                var key = arr[i];
                $("#" + key).html(state[key]);
            }
            $("#throughput").html(state["throughput"].toFixed(2));
            this._set_registers(state["registers"]);
            this._set_pipeline(state["pipeline"]);
            this._set_memory(state["memory"]);
        }
        else {
            this._running = false;
        }
    },
    
    _refresh: function(data) {
        mips._data = data.result;
        mips.goto(0);
    },
    
    _set_registers: function(registers) {
        for (var i in registers) {
            var register_field = $('#r' + i);
            var value = register_field.html();
            var color = 'black';
            register_field.html(registers[i]);
            
            register_field.css('color', function() {
                if (value != registers[i]) {
                    color = 'red';
                }
                return color;
            });
        }
    },
    
    _set_pipeline: function(pipeline) {
        var flags_string = function(flags) {
            var s = ""
            for (var key in flags) {
                s += key.toLowerCase() + ": " + flags[key] + "<br />"
            }
            return s;
        };
        $("#if").html(pipeline[0].text);
        $("#if_flags").html(flags_string(pipeline[0].flags));
        $("#id_").html(pipeline[1].text);
        $("#id_flags").html(flags_string(pipeline[1].flags));
        $("#ex").html(pipeline[2].text);
        $("#ex_flags").html(flags_string(pipeline[2].flags));
        $("#mem").html(pipeline[3].text);
        $("#mem_flags").html(flags_string(pipeline[3].flags));
        $("#wb").html(pipeline[4].text);
        $("#wb_flags").html(flags_string(pipeline[4].flags));
    },

    _set_memory: function(memory) {
        for (var i=0; i < 4; i++) {
            if (memory[i]) {
                $("#memory_addr_" + i).html(memory[i][1]);
                $("#memory_value_" + i).html(memory[i][2]);
            }
        }
    }
}


function handleFileSelect(files) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var data = e.target.result;
        $("#filedata").html(data);
    };
    reader.readAsText(files[0]);
}

