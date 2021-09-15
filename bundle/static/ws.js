class WS {
    constructor(onMessage){
        this.ws = new WebSocket("ws://127.0.0.1:5678");
        this.onMes = onMessage

        this.ws.onopen = () =>  { 
            this.send(JSON.stringify({'step':'init'}));
        };
        this.ws.onmessage = (evt) => {
            let data = JSON.parse(evt.data);
            this.onMessage(data)
        }
    }

    start(taskId){
        this.send(JSON.stringify({'step':'start','taskId': taskId || 0}));
    }

    next(){
        this.send(JSON.stringify({'step':'next'})); 
    }

    send(info){
        this.ws.send(info)
    }

    onMessage(data){
        this.onMes(data)
    }
}


export default WS