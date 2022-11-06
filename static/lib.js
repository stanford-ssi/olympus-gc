

var socket = io.connect({ transports: ['websocket'] });

//elements can add themselves to list to update on new data
new_data_callbacks = [];
// new_data_callbacks = [() => { console.log("got data", slate) }];
slate = {};

metaslate = {};

socket.on("new", (update) => {
    slate = update
    for (func of new_data_callbacks) {
        try {
            func();
        } catch (error) {
            console.error("failed new_data_callback");
            console.error(error);
        }
    }
});

socket.on("deliver-metaslate", (update) => {
    metaslate = update
});

function send_command(cmd, target = "cmd") {
    //TODO: check if it is editable

    if (Cookies.get('auth')) {
        out = { "auth": Cookies.get('auth') }
        out[target] = cmd;
        socket.emit("cmd", out);
    } else {
        alert("Observers can't send commands");
    }

}

function get_data(path) {
    path = path.split(".")
    node = slate
    for (item of path) {
        node = node[item]
    }
    return node
}