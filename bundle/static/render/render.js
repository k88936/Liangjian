import Robot from './robot.js'
import Shelf from './shelf.js'
import Cell from './cell.js'
import Line from './line.js'
import HotMap from './hotmap.js'

class Render{
    constructor(viewport,selectCallback){
        this.viewport = viewport

        this.robotList = {}
        this.shelfList = {}

        this.selectEle = null
        this.selectedCallback = selectCallback

        this.renderCell = new Cell()

        this.isShowPath = false
        this.isShowHotMap = false
    }

    showPath(bol){
        this.isShowPath = bol
    }

    showHotMap(bol){
        this.isShowHotMap = bol
        if(!bol){
            this.hotMap.clearHotMap()
        }
    }

    init(){
        this.robotCon = new PIXI.Container()
        this.robotCon.zIndex = 20
        this.cellCon = new PIXI.Container()
        this.cellCon.zIndex = 1
        this.shelfCon = new PIXI.Container()
        this.shelfCon.zIndex = 30
        this.lineCon = new PIXI.Container()
        this.lineCon.zIndex = 10
        this.targetCon = new PIXI.Container()
        this.targetCon.zIndex = 2

        this.viewport.addChild(this.cellCon)
        this.viewport.addChild(this.lineCon)
        this.viewport.addChild(this.robotCon)
        this.viewport.addChild(this.shelfCon)
        this.viewport.addChild(this.targetCon)
    }

    reset(){
        this.clearCon(this.cellCon)
        this.clearCon(this.lineCon)
        this.clearCon(this.robotCon)
        this.clearCon(this.shelfCon)
        this.clearCon(this.targetCon)
        this.robotList = {}
        this.shelfList = {}

        this.selectEle = null

        this.init()
    }

    render(data){
        this.reset()
        data = JSON.parse(JSON.stringify(data))
        console.log('data: ', data);
        
        this.hotMap = new HotMap({
            width:data.width * 55 + 55,
            height:data.height * 55 + 55,
        })
        if(data&&data.mapCells){
            this.renderCells(data.mapCells)
        }
        if(data&&data.robots){
            this.renderRobots(data.robots)
        }
        if(data&&data.shelves){
            this.renderShelves(data.shelves)
        }
    }

    renderCells(data){
        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            const cell = this.renderCell.render(item)
            const [x,y] = this.countXY(item.index)
            cell.x = x
            cell.y = y
            this.cellCon.addChild(cell)
        }
    }
    renderRobots(data){
        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            const [x,y] = this.countXY(item.locationIndex)
            item.locationIndex = [x,y]
            item.color = this.randomColor()
            let robot = new Robot(item, this.selectCallback.bind(this,'robot'))
            this.robotList[item.robotId] = robot
            this.robotCon.addChild(robot.container)
        }
    }
    renderShelves(data){
        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            const [x,y] = this.countXY(item.placement)
            item.placement = [x,y]
            let shelf = new Shelf(item, this.selectCallback.bind(this,'shelf'))
            this.shelfList[item.code] = shelf
            this.shelfCon.addChild(shelf.container)
        }
    }
    renderLines(paths, color=0x666666){
        let line = new Line(paths, color)
        this.lineCon.addChild(line.Container)
    }

    renderHotMap(){
        if(!this.isShowHotMap) return
        let data = {}
        let robots = Object.values(this.robotList)
        for (let i = 0; i < robots.length; i++) {
            const robot = robots[i];
            for (let key in robot.movedList){
                if(!data[key]){
                    data[key] = robot.movedList[key]
                }else{
                    data[key] = data[key] + robot.movedList[key]
                }
            }
        }
        
        let result = []
        let space = 24
        let max = 0
        for (let key in data){
            const [x,y] = this.countXY(key.split(','))
            if(data[key] > max){
                max = data[key]
            }
            result.push({
                x: + x + space,
                y: + y + space,
                value: data[key]
            })
        }

        this.hotMap.creatHotInit({
            data:result,
            max,
        })
        this.hotMap.Container.x = -space
        this.hotMap.Container.y = -space
        this.targetCon.addChild(this.hotMap.Container)
    }

    update(data){
        data = JSON.parse(JSON.stringify(data))
        this.clearCon(this.lineCon)
        this.lineCon = new PIXI.Container()
        this.lineCon.zIndex = 10
        this.viewport.addChild(this.lineCon)

        if(data&&data.robots){
            this.updateRobots(data.robots)
            this.renderHotMap()
        }
        if(data&&data.shelves){
            this.updateShelves(data.shelves)
        }
    }

    updateRobots(data){
        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            const {locationIndex, nextIndex, position} = item
            const [newx,nexy]=this.countPosition(locationIndex, nextIndex, position)
            const [x,y] = this.countXY([newx,nexy])
            item.locationIndex = [x,y]
            this.robotList[item.robotId].update(item)


            if(this.isShowPath){
                if(item.assignedPath){
                    item.assignedPath[0] = [newx,nexy]
                    this.renderLines(item.assignedPath,null)
                }
    
                item.updatePath && this.renderLines(item.updatePath, this.robotList[item.robotId].data.color)
            }
        }
    }

    updateShelves(data){
        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            if(!item.placement){
                item.placement = this.robotList[item.robotId].data.locationIndex
            }else{
                item.placement = this.countXY(item.placement)
            }
            this.shelfList[item.code].update(item)
        }
    }

    clearCon(container){
        container && container.destroy({
            children: true,
            texture: true,
            baseTexture: true
        })
    }

    selectCallback(type, data){
        this.selectEle && this.selectEle.highLight()
        this.selectEle = data
        this.selectEle.highLight()

        this.selectedCallback(type, data)
    }

    randomColor(){
        // var colorValue = [0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f'];
        var colorValue = [4, 5,6,7,8,9,'a','b','c','d'];
        var s = "0x";
        for (var i=0;i<6;i++) {
            if(s!=='0xffffff'){
                s+=colorValue[Math.floor(Math.random()*8)];
            }
        }
        return s;
    }

    countXY([x,y]){
        const space = 55
        return [(x * space).toFixed(2), (y * space).toFixed(2)]
    }

    countPosition(location,next,position){
        let newx = location[0]
        let newy = location[1]
        if(next && location.toString() !== next.toString()){
            newx = location[0] + (next[0] - location[0]) * position
            newy = location[1] + (next[1] - location[1]) * position
        }

        return [newx,newy]
    }
}

export default Render