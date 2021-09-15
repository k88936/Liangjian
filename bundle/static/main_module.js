
import RenderRobot from './robot.js'
import RenderShelf from './shelf.js'
import RenderCell from './cell.js'
import EndCell from './targetCell.js'

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
    autoDensity: true,
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
        ins.Container.children[0].tint = ins.color
        ins.targetContainer.alpha = 0
    }
    messageList.robotSelected = robot.data.robotId
    robot.Container.children[0].tint = 0xcccc00
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
// 选中工作站操作
function selectedStation(data){
    let result = ''
    for (let i = 0; i < Object.keys(data).length; i++) {
        const key = Object.keys(data)[i];
        result +=`<p>${key}: ${JSON.stringify(data[key])}</p>`
    }
    document.querySelector('.stationInfo').innerHTML = result
}
//显示机器人和货架信息
function renderShelfInfo(){
    if(messageList.shelfSelected == ''){
        document.querySelector('.shelfInfo').innerHTML = ''
        return
    }
    let info = messageList.ShelfList[messageList.shelfSelected]
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
    
    let info = messageList.RobotList[messageList.robotSelected]
    const {data} = info
    let result = ''
    for (let i = 0; i < Object.keys(data).length; i++) {
        const key = Object.keys(data)[i];
        result +=`<p>${key}: ${JSON.stringify(data[key])}</p>`
    }
    document.querySelector('.robotInfo').innerHTML = result
}
function initMap(datas){
    //初始化渲染格子画布
    if(datas&&datas.mapCells){
        for (let i = 0; i < datas.mapCells.length; i++) {
            const item = datas.mapCells[i];
            messageList.CellList[item.cellCode] = new RenderCell(item, selectedStation);
            viewport.addChild(messageList.CellList[item.cellCode].Container)
        }
    }
    //机器人
    if(datas&&datas.robots){
        for (let i = 0; i < datas.robots.length; i++) {
            const item = datas.robots[i];
            messageList.RobotList[item.robotId] = new RenderRobot(item, selectedRobot);
            viewport.addChild(messageList.RobotList[item.robotId].lineContainer)
            viewport.addChild(messageList.RobotList[item.robotId].targetContainer)
            viewport.addChild(messageList.RobotList[item.robotId].Container)
        }
    }
    // //终点
    if(datas&&datas.task){
        for(let key in datas.task){
            const item = datas.task[key];
            const robotColor = messageList.RobotList[item.robot_id].color;
            messageList.endList[item.robot_id] = new EndCell(item,robotColor);
            viewport.addChild(messageList.endList[item.robot_id].Container);
        }
    }
    // //货架
    if(datas&&datas.shelves){
        for (let i = 0; i < datas.shelves.length; i++) {
            const item = datas.shelves[i];
            if(!item.placement){
                item.placement = messageList.RobotList[item.robotId].data.locationIndex
            }
            messageList.ShelfList[item.code] = new RenderShelf(item,selectedShelf);
            viewport.addChild(messageList.ShelfList[item.code].Container)
            viewport.addChild(messageList.ShelfList[item.code].targetContainer)
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
            console.log(messageList.RobotList[item.robotId].lineContainer)
            viewport.addChild(messageList.RobotList[item.robotId].lineContainer)
        }

        renderRobotInfo()
    }
    //货架
    if(datas&&datas.shelves){
        for (let i = 0; i < datas.shelves.length; i++) {
            const item = datas.shelves[i];

            if(!item.placement){
                item.placement = [messageList.RobotList[item.robotId].Container.x,messageList.RobotList[item.robotId].Container.y]
            }else{
                item.placement = countXY(item.placement)
            }
            
            messageList.ShelfList[item.code].update(item)
        }
    }
}

function countXY([x,y]){
    const space = 55
    return [x * space,y*space]
}
