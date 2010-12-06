TICKS = 100;

URL_BASE = '/mips'

var mips = {
    _data: [],
    _current_position: null,
    _running: false,

    compare: function(text, data_forwarding) {
        $.ajax({
            url:URL_BASE + '/compare',
            data: {"text":text},
            success: mips._compare_callback,
            dataType: "json",
            type: "POST"
        });
    },

    compile: function(text, data_forwarding) {
        $.ajax({
            url:URL_BASE + '/compile',
            data: {"text":text},
            success: mips._compile_callback,
            dataType: "json",
            type: "POST"
        });
    },

    execute: function(text, data_forwarding) {
        var bool = (data_forwarding) ? 1 : 0;
        $.ajax({
            url:URL_BASE + '/execute',
            data: {"text":text, "data_forwarding":bool},
            success: mips._execute_callback,
            dataType: "json",
            type: "POST"
        });
    },

    next: function() {
        if (this._running) {
            TICKS /= 2;
        }
        else {
            if (this._current_position < this._data.length - 1) {
                this.goto(++this._current_position);
            }
            else {
                this._running = false;
            }
        }
    },
    
    prev: function() {
        if (this._running) {
            TICKS *= 2;
        }
        else {
            if (this._current_position > 0) {
                this.goto(--this._current_position);
            }
            else {
                this._running = false;
            }
        }
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
            if (mips._current_position < mips._data.length - 1) {
                mips.goto(++mips._current_position);
            }
            else {
                mips._running = false;
            }
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
            $("#throughput").html(state.throughput.toFixed(2));
            this._set_registers(state.registers);
            this._set_pipeline(state.pipeline);
            this._set_memory(state.memory);
            this._set_progress(state.clock, this._data.length - 1);
        }
        else {
            this._running = false;
        }
    },
    
    _compare_callback: function(data) {
        result = "Clocks:\n"
        result += data.slower_mips.clocks;
        result += " x ";
        result += data.faster_mips.clocks;
        result += "\nProdutividade:\n";
        result += data.slower_mips.throughput.toFixed(2);
        result += " x ";
        result += data.faster_mips.throughput.toFixed(2);
        alert(result);
    },

    _compile_callback: function(data) {
        bytecode.value = data.result;
    },
    
    _execute_callback: function(data) {
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
        var flags_string = function(flags, keys) {
            var s = "";
            for (var key in flags) {
                s += key.toLowerCase() + ": " + flags[key] + "<br />";
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
    },
    
    _set_progress: function(clock, total) {
        $("#range")[0].value = clock;
        $("#range")[0].max = total;
        $("#range_text").html(clock + " / " + total);
    },
}

function handleFileSelect(files) {
    var reader = new FileReader();
    reader.onload = function(e) {
        bytecode.value = e.target.result;;
    };
    reader.readAsText(files[0]);
}

