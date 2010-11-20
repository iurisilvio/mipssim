var mips = {
    _data: [],
    _current_position: null,

    execute: function(text) {
        self = this;
        $.ajax({
            url:'/mips/execute',
            data: {"text":bytecode.value},
            success: self._refresh,
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
    
    },
    
    pause: function() {
    
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
        self._data = data.result;
        self.goto(0);
    },
    
    _set_registers: function(registers) {
        for (var i in registers) {
            $('#r' + i).html(registers[i]);
        }
    },
    
    _set_pipeline: function(pipeline) {
        $("#if").html(pipeline.if.text);
        $("#_id").html(pipeline.id.text);
        $("#ex").html(pipeline.ex.text);
        $("#mem").html(pipeline.mem.text);
        $("#wb").html(pipeline.wb.text);

    },
}
