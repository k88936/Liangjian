let ws = new WebSocket("ws://127.0.0.1:5678");
let messageList = {
    CellList:{},//画布格子
    RobotList:{},//机器人
    ShelfList:{},//货架
    lineList:{},//线路
    alineList:{},// assingedPath
    cellSelected:"",//选中的格子
    robotSelected:"",//选中额机器人
    shelfSelected:"",//选中的货架
    endList:{},//机器人终点格子
    num:1,//判断是start还是next
    isChecked:false,//是否显示路线
    timer:null,//next定时器
    time:300,//运行速度
    isStart:false,//是否点击开始
    tabName:"robot"
}
const CELL_COLOR = {
    'QUEUE_CELL': '0xEDE2BE',
    'STATION_CELL': '0xF29361',
    'TURN_CELL': '0xD7C99F',
    'OMNI_DIR_CELL': '0xD2E5F5',
    'SHELF_CELL': '0x8BD4DB',
    'BLOCKED_CELL': '0xcccccc'
}
let mapDom = document.getElementById('map')
let App = new PIXI.Application({
    width: mapDom.offsetWidth,
    height: mapDom.offsetHeight,
    antialias: true,
    })  
App.ticker.maxFPS = 20
let viewport = new Viewport.Viewport({
    screenWidth: mapDom.offsetWidth,
    screenHeight: mapDom.offsetHeight,
    passiveWheel: false,
    divWheel: mapDom,
    interaction: App.renderer.plugins.interaction,
})
App.renderer.backgroundColor = 0xf2f2f2
App.stage.addChild(viewport)
viewport.drag().pinch().wheel({
    percent: 0.01,
})
viewport.sortableChildren = true
mapDom.appendChild(App.view)

//初始化
initWS()
//点击选择展示地图
startWS()
//执行next
nextWSBtn()
//暂时线路
showLine()
//重置地图
resetWS()
//选择时间
chooseTime()
//切换信息内容
tabsInfo()

let infomation = {
    selectInfo:{},
    shelfInfo:{}
}
function initWS(){
    ws.onopen = function(evt) { 
        ws.send(JSON.stringify({'step':'init'}));
    };
    ws.onmessage = function(evt) {
        let data = JSON.parse(evt.data);
        //初始化地图
        if(data.type=="init"){
            let selectMapDom = document.getElementById('mapSelect');
            for(var i = 0; i < data.data.taskLength; i++){
                let options = document.createElement("option");
                options.innerHTML = i + 1;
                options.setAttribute('value',i);
                selectMapDom.appendChild(options); 
            }
            ws.send(JSON.stringify({'step':'start','taskId':0}));
        }
        //选择时间
        if(data.type == "start"){
            if(data.code == 1){
                ws.send(JSON.stringify({'step':'start','taskId':0}));
            }else{
                initMap(data.data)
            }
        }
        if(data.data&&data.data.result != undefined){
            document.querySelector(".result").innerHTML = data.data.result
            clearTimeout( messageList.timer)
            return
        }else{
            document.querySelector(".result").innerHTML = ''
        }
        if(data.type == "next"&&data.data){
            let datas = data.data;
            updateMap(datas);
            messageList.isStart?nextWS():"";
            document.querySelector(".currentTime").innerHTML = datas.timestamp||"";
        }
    }
}
//点击选择地图
function startWS(){
    let selectMapDom = document.getElementById('mapSelect');
    let choose = document.querySelector('.choose');
    choose.addEventListener("click",function(){
        var index = selectMapDom.selectedIndex;
        var value = Number(selectMapDom.options[index].value);
        ws.send(JSON.stringify({'step':'start','taskId':value}));
        clear();
    })
}
//点击开始暂停
function nextWSBtn(){
    let start = document.querySelector(".start")
    start.addEventListener('click',(e)=>{
        messageList.isStart = !messageList.isStart
        if(messageList.isStart){
            start.innerText = "暂停"
            ws.send(JSON.stringify({'step':'next'}))
        }else{
            clearTimeout(messageList.timer)
            start.innerText = "开始"
        }
    })
}
//next请求
function nextWS(){
    clearTimeout( messageList.timer);
    messageList.timer = setTimeout(()=>{
        ws.send(JSON.stringify({'step':'next'})); 
    },messageList.time);
}
//清楚正在进行的动作
function clear(){
    messageList.isStart = false;
    clearTimeout( messageList.timer);
    document.querySelector(".start").innerHTML = '开始';
    viewport.children = [];
    messageList.isChecked = false;
    document.querySelector('.checkbox').checked = false;
    document.querySelector(".currentTime").innerHTML = "";
    messageList.robotSelected = ""
}
//重置
function resetWS(){
    let reset = document.querySelector(".reset");
    let selectMapDom = document.getElementById('mapSelect');
    reset.addEventListener('click',(e)=>{
        var index = selectMapDom.selectedIndex;
        var value = Number(selectMapDom.options[index].value);
        ws.send(JSON.stringify({'step':'start','taskId':value}));
        clear();
    })
}
//点击选择时间
function chooseTime(){
    let selectTimeDom = document.querySelector(".selectTime");
    selectTimeDom.addEventListener("change",function(){
        var index = selectTimeDom.selectedIndex;
        var value = Number(selectTimeDom.options[index].value);
        messageList.time = value;
    })
}
//点击显示线路
function showLine(){
    let checkbox = document.querySelector('.checkbox');
    checkbox.addEventListener('click',function(){
        checkbox.checked?messageList.isChecked = true:messageList.isChecked = false;
    })
}
//切换信息内容
function tabsInfo(){
    let titles = document.querySelectorAll(".titles");
    let tabs = document.querySelectorAll(".tab");
    for(var i = 0; i < titles.length; i++) {
        titles[i].index = i;
        titles[i].onclick = function() {
            for(var j = 0; j < titles.length; j++) {
                titles[j].className = "";
            }
            this.className = "active";
            for(var k = 0; k < tabs.length; k++) {
                tabs[k].style.display = "none";
            }
            tabs[this.index].style.display = "block";
        }
    }
}

// 选中机器人操作
function selectedRobot(robot){
    if(messageList.robotSelected){
        let ins = messageList.RobotList[messageList.robotSelected]
        ins.Container.children[0].tint = 0xFFFFFF
        ins.targetContainer.alpha = 0
    }
    messageList.robotSelected = robot.data.robotId
    robot.Container.children[0].tint = 0xde553f
    robot.targetContainer.alpha = 1
    renderRobotInfo()
}
// 选中货架操作
function selectedShelf(shelf){
    if(messageList.shelfSelected){
        let ins = messageList.ShelfList[messageList.shelfSelected]
        ins.Container.tint = 0xFFFFFF
        ins.targetContainer.alpha = 0
    }
    messageList.shelfSelected = shelf.data.code
    shelf.Container.tint = 0xde553f
    shelf.targetContainer.alpha = 1

    renderShelfInfo()
}
//显示机器人和货架信息
function renderShelfInfo(){
    if(messageList.shelfSelected == ''){
        document.querySelector('.shelfInfo').innerHTML = ''
        return
    }
    info = messageList.ShelfList[messageList.shelfSelected]
    const {data} = info
    let result = ''
    for (let i = 0; i < Object.keys(data).length; i++) {
        const key = Object.keys(data)[i];
        result +=`<p>${key}: ${JSON.stringify(data[key])}</p>`
    }
    document.querySelector('.shelfInfo').innerHTML = result
}
function renderRobotInfo(){
    if(messageList.robotSelected == ''){
        document.querySelector('.robotInfo').innerHTML = ''
        return
    }
    info = messageList.RobotList[messageList.robotSelected]
    const {data} = info
    let result = ''
    for (let i = 0; i < Object.keys(data).length; i++) {
        const key = Object.keys(data)[i];
        result +=`<p>${key}: ${JSON.stringify(data[key])}</p>`
    }
    document.querySelector('.robotInfo').innerHTML = result
}
function initMap(datas){
    // let data = datas.sim
    //初始化渲染格子画布
    if(datas&&datas.mapCells){
        for (let i = 0; i < datas.mapCells.length; i++) {
            const item = datas.mapCells[i];
            messageList.CellList[item.cellCode] = new RenderCell(item);
            messageList.CellList[item.cellCode].render();
        }
    }
    //机器人
    if(datas&&datas.robots){
        for (let i = 0; i < datas.robots.length; i++) {
            const item = datas.robots[i];
            messageList.RobotList[item.robotId] = new RenderRobot(item);
            messageList.lineList[item.robotId] = new RenderLine();
            messageList.alineList[item.robotId] = new RenderLine();
        }
        
    }
    //终点
    if(datas&&datas.task){
        for(let key in datas.task){
            const item = datas.task[key];
            const robotColor = messageList.RobotList[item.robot_id].color;
            
            messageList.endList[item.robot_id] = new EndCell(item);
            messageList.endList[item.robot_id].render(robotColor);
        }
    }
    //货架
    if(datas&&datas.shelves){
        for (let i = 0; i < datas.shelves.length; i++) {
            const item = datas.shelves[i];
            messageList.ShelfList[item.code] = new RenderShelf(item);
        }
    }else{
        let dom = document.querySelector('.shelf')
        if(dom) dom.remove()
    }

    viewport.fitWorld()

    viewport.x = (mapDom.offsetWidth - viewport.width) / 2 + 50*viewport.scaled/2
    viewport.y = (mapDom.offsetHeight - viewport.height) / 2 + 50*viewport.scaled/2

}
//更新地图
function updateMap(datas){
    //机器人
    if(datas&&datas.robots){
        for (let i = 0; i < datas.robots.length; i++) {
            const item = datas.robots[i]
            messageList.RobotList[item.robotId].update(item)
        }

        renderRobotInfo()
    }
    //货架
    if(datas&&datas.shelves){
        for (let i = 0; i < datas.shelves.length; i++) {
            const item = datas.shelves[i];
            
            messageList.ShelfList[item.code].update(item)
        }
    }
}
class RenderCell{
    constructor (data) {
        this.Container = new PIXI.Graphics()
        this.data = data
        this.Container.name = 'CELL'
        this.selected = ""
        this.width = 50
    }
    render(){
        this.Container.beginFill(CELL_COLOR[this.data.cellType]||'0xD2E5F5')
        this.Container.drawRect(-this.width/2, -this.width/2, this.width, this.width)
        this.Container.endFill()
        this.Container.interactive = true;
        const [x,y] = countXY(this.data.index)
        this.Container.x = x
        this.Container.y = y
        this.Container.zIndex = 1
        viewport.addChild(this.Container)
        // this.select(this.data.cellCode)
    }
    select(cell){
        let selectContainer = messageList.CellList[cell].Container
        selectContainer.on("pointerdown", ()=>{
            if( messageList.cellSelected){
                messageList.CellList[messageList.cellSelected].Container.tint = 0xFFFFFF
            }
            messageList.cellSelected = cell
            selectContainer.tint = 0xde553f
        });
    }
}
//机器人终点路线
class EndCell{
    constructor (data) {
        this.Container = new PIXI.Graphics()
        this.data = data
        this.Container.name = 'EndCell'
        this.width = 50
        this.style = {
            fontFamily: 'Arial',
            fontSize: '20px',
            fontWeight: 'bold',
            fill: '#fff',
            align: 'center'
        }; 
    }
    render(robotColor){
        
        const basicText = new PIXI.Text(this.data.robot_id,this.style)
        basicText.anchor.set(0.5)
        // this.Container.interactive = true;
        this.Container.beginFill(Number(robotColor))
        
        this.Container.drawRect(-this.width/2,-this.width/2, this.width, this.width)
        this.Container.endFill()
        const [x,y] = countXY([this.data.destX,this.data.destY])
        this.Container.x = x
        this.Container.y = y
        this.Container.zIndex = 3
        switch (this.data.endDirection) {
            case 0:
                this.Container.rotation = 0.5*Math.PI
                break;
            case 1:
                this.Container.rotation = 0
                break;
            case 2:
                this.Container.rotation = 1.5*Math.PI
                break;
            case 3:
                this.Container.rotation = Math.PI
                break;
        }
        this.Container.addChild(basicText)
        viewport.addChild(this.Container)
    }
}
class RenderRobot{
    constructor (data) {
        this.style = {
            fontFamily: 'Arial',
            fontSize: '16px',
            fontWeight: 'bold',
            fill: '#fff',
        };
        this.Container = new PIXI.Sprite()
        this.robotContainer = new PIXI.Graphics()
        this.TextContainer = new PIXI.Text(data.robotId,this.style)
        this.TextContainer.anchor.set(0.5)

        this.targetContainer = new PIXI.Graphics()
        this.data = data
        this.Container.name = 'ROBOT'
        this.robotContainer.name = "ROBOTCHILD"
        this.TextContainer.name = "ROBOTTEXT"
        this.Container.interactive = true
        this.color = this.randomColor()
        this.render()
        this.renderTarget()
    }

    renderTarget(){
        const { destIndex } = this.data
        if(!destIndex) return
        let width = 50
        this.targetContainer.zIndex = 3;
        this.targetContainer.alpha = 0;
        viewport.addChild(this.targetContainer)

        this.targetContainer.beginFill(0xFF8C00)
        const [drawX,drawY] = countXY(destIndex)
        this.targetContainer.drawRect(drawX-width/2,drawY-width/2, width, width)
        this.targetContainer.endFill();
    }
    render(){
        const width = 20
        this.robotContainer.beginFill(this.color)
        this.robotContainer.lineStyle(1, 0xFFFFFF)
        this.robotContainer.drawCircle(0, 0, width)
        this.robotContainer.endFill()
        const [x,y] = this.countPosition(this.data.locationIndex)
        this.Container.x = x
        this.Container.y = y
        this.Container.zIndex = 4
        this.Container.addChild(this.robotContainer)
        this.Container.addChild(this.TextContainer)
        viewport.addChild(this.Container)
        this.direction(this.data.direction)
        this.select()
    }
    update(value){ 
        const [x,y] = this.countPosition(value.locationIndex,value.nextIndex,value.position)
        this.Container.x = x
        this.Container.y = y
        this.direction(value.direction)
        this.data = value
        console.log(value)
        if(value.updatePath){
            messageList.lineList[value.robotId].render(value.updatePath,this.color)  
        }else{
            messageList.lineList[value.robotId].render([],this.color)  
        }
        //显示机器人路径
        if(value.assignedPath){
            messageList.alineList[value.robotId].render(value.assignedPath,0xff0000)  
        }
    }
    select() {
        this.Container.on("pointerdown", ()=>{
            selectedRobot(this)
        });
        
    }
    countPosition(location,next,position){
        let newx = location[0]
        let newy = location[1]
        if(next && location.toString() !== next.toString()){
            newx = location[0] + (next[0] - location[0]) * position
            newy = location[1] + (next[1] - location[1]) * position
        }

        return countXY([newx,newy])
    }
    randomColor(){
        // var colorValue = [0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f'];
        var colorValue = [5,6,7,8,9,'a','b','c'];
        var s = "0x";
        for (var i=0;i<6;i++) {
            if(s!=='0xffffff'){
                s+=colorValue[Math.floor(Math.random()*8)];
            }
        }
        return s;
    }
    direction(direction){
        switch (direction) {
            case 0:
                this.Container.rotation = 0.5*Math.PI
                break;
            case 1:
                this.Container.rotation = 0
                break;
            case 2:
                this.Container.rotation = 1.5*Math.PI
                break;
            case 3:
                this.Container.rotation = Math.PI
                break;
        }
    }
}
class RenderShelf{
    constructor (data) {
        this.Container = new PIXI.Graphics()
        this.targetContainer = new PIXI.Graphics()
        this.data = data
        this.Container.name = 'SHELF'
        this.selected = ""
        this.render()
        this.renderTarget()
    }
    showTarget(isShow){
        if(isShow){
            this.targetContainer.alpha = 1
        }else{
            this.targetContainer.alpha = 0
        }
    }
    render(){
//         const [lax,lay] = countXY(this.data.placement)
//         const [x,y] = this.data.placement
        this.Container.beginFill(0x4682B4);
        this.Container.drawPolygon(this.drawShelf());
        this.Container.endFill();
        this.Container.interactive = true;
        if(this.data.placement){
            const [x,y] = countXY(this.data.placement)
            this.Container.x = x
            this.Container.y = y
        }else{
            this.Container.x = messageList.RobotList[this.data.robotId].Container.x
            this.Container.y = messageList.RobotList[this.data.robotId].Container.y
        }
        this.Container.zIndex = 5;
        viewport.addChild(this.Container);
        this.select(this.data.code)
    }
    renderTarget(){
        let width = 50
        this.targetContainer.zIndex = 3;
        this.targetContainer.alpha = 0;
        viewport.addChild(this.targetContainer)

        const {targetArea} = this.data

        this.targetContainer.beginFill(0xff4444)
        for (let i = 0; i < targetArea.length; i++) {
            const {x,y} = targetArea[i];
            const [drawX,drawY] = countXY([x,y])
            this.targetContainer.drawRect(drawX-width/2,drawY-width/2, width, width)
        }
        this.targetContainer.endFill();
    }
    update(value){
        if(value.placement){
            const [x,y] = countXY(value.placement)
            this.Container.x = x
            this.Container.y = y
        }else{
            
            this.Container.x = messageList.RobotList[value.robotId].Container.x
            this.Container.y = messageList.RobotList[value.robotId].Container.y
        }
        this.data = value
    }
    drawShelf(){
        let x = 0
        let y = 0
        let width = 40
        let space = 5
        const points = [
            x, y - space / 2,
            x + width / 2 - space, y - space / 2,
            x + width / 2 - space, y - width / 2,
            x + width / 2, y - width / 2,
            x + width / 2, y + width / 2,
            x + width / 2 - space, y + width / 2,
            x + width / 2 - space, y + space / 2,
            x - width / 2 + space, y + space / 2,
            x - width / 2 + space, y + width / 2,
            x - width / 2, y + width / 2,
            x - width / 2, y - width / 2,
            x - width / 2 + space, y - width / 2,
            x - width / 2 + space, y - space / 2,
        ]
        return points
    }
    select() {
        this.Container.on("pointerdown", ()=>{
            selectedShelf(this)
        });
    }
    highLight(code){
        let highlightArr =  messageList.ShelfList[code].data.assignedPath
        for(let i = 0; i < highlightArr.length-1; i++){
            let item = highlightArr[i].code
             messageList.ShelfList[item].tint = 0xde553f
        }
    }
}
class RenderLine{
    constructor () {
        this.lineContainer = new PIXI.Graphics()
        this.lineContainer.name = 'LINE'
        this.bezierContainer = new PIXI.Graphics()
        this.lineContainer.name = 'BEZIER'
    }
    render(data,robotColor){
        this.lineContainer.clear()
        if(messageList.isChecked){
            for (let i = 0; i < data.length-1; i++) {
                this.drawLine(data[i],data[i+1],robotColor)
            }
        }else{
            this.lineContainer.clear()
        }
    }
    drawLine(start,end,robotColor){
        const [startx,starty] = countXY(start);
        const [endx,endy] = countXY(end);
        this.lineContainer.lineStyle(4, robotColor||'0xCC0000', 1);
        this.lineContainer.moveTo(startx, starty);
        this.lineContainer.lineTo(endx,endy);
        this.lineContainer.zIndex = 2;
        viewport.addChild(this.lineContainer);
    }
    drawBezier(start,next,end){
        const [startx,starty] = countXY(start)
        const [nextx,nexty] = countXY(next)
        const [endx,endy] = countXY(end)
        bezierContainer.lineStyle(4, 0x66CCFF, 1);
        bezierContainer.moveTo(startx, starty); //起点
        bezierContainer.bezierCurveTo(startx, starty, nextx, nexty, endx, endy); 
        viewport.addChild(this.bezierContainer);
    }
}

function countXY([x,y]){
    const space = 55
    return [x * space,y*space]
}
