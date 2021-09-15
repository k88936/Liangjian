import Line from './line.js'
export default class RenderRobot{
    constructor (data,selectedRobot) {
        this.maxUpdataLineLength = 10000
        this.selectedRobot = selectedRobot
        this.Container = new PIXI.Sprite()
        this.robotContainer = new PIXI.Graphics()

        this.targetContainer = new PIXI.Graphics()

        this.lineContainer = new PIXI.Container()

        this.data = data
        this.color = this.randomColor()
        this.style = {
            fontFamily: 'Arial',
            fontSize: '16px',
            fontWeight: 'bold',
            fill: 0xffffff,
        };

        this.TextContainer = new PIXI.Text(data.robotId,this.style)
        this.TextContainer.anchor.set(0.5)


        this.Container.interactive = true
        this.lastPath = []
        this.render()
        this.renderTarget()
    }
    render(){
        let texture = PIXI.Texture.from('./static/robot.svg');
        this.robotContainer = new PIXI.Sprite(texture);
        this.robotContainer.scale.set(0.4)
        this.robotContainer.anchor.set(0.5)
        this.robotContainer.tint = this.color 

        const [x,y] = this.countXY(this.countPosition(this.data.locationIndex))
        this.Container.x = x
        this.Container.y = y
        this.Container.zIndex = 4
        this.Container.addChild(this.robotContainer)
        this.Container.addChild(this.TextContainer)
        // viewport.addChild(this.Container)
        this.direction(this.data.direction)
        this.select()
    }

    renderTarget(){
        const { destIndex } = this.data
        if(!destIndex) return
        let width = 50
        this.targetContainer.alpha = 0;
        // viewport.addChild(this.targetContainer)

        this.targetContainer.beginFill(0x006cee)
        const [drawX,drawY] = this.countXY(destIndex)
        this.targetContainer.drawRect(drawX-width/2,drawY-width/2, width, width)
        this.targetContainer.endFill();
    }

    renderLastLine(){


    }

    renderLine(){
        this.lineContainer.destroy({
            children: true,
            texture: true,
            baseTexture: true
          })
        this.lineContainer = new PIXI.Container()
        if(this.data && this.data.assignedPath){
            const {locationIndex,nextIndex,position} = this.data
            this.data.assignedPath[0] = this.countPosition(locationIndex,nextIndex,position)
            let a = new Line(this.data.assignedPath,0x666666)
            this.lineContainer.addChild(a.Container)
        }
        if(this.data && this.data.updatePath){
            let path = []
            if(this.data.updatePath.length > this.maxUpdataLineLength){
                path = this.data.updatePath.slice(0,this.maxUpdataLineLength)
            }else{
                path = this.data.updatePath
            }
            console.log('path: ', path);
            let a = new Line(path,this.color)
            this.lineContainer.addChild(a.Container)
        }
    }
    update(value){
        const [newx,nexy]=this.countPosition(value.locationIndex,value.nextIndex,value.position)
        const [x,y] = this.countXY([newx,nexy])
        this.Container.x = x
        this.Container.y = y
        this.direction(value.direction)
        this.data = value

        this.renderLine(value)
    }
    select() {
        this.Container.on("pointerdown", ()=>{
            this.selectedRobot(this)
        });
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
    countXY([x,y]){
        const space = 55
        return [x * space, y * space]
    }
}