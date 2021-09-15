import Line from './line.js'
export default class RenderRobot{
    constructor (data, selectCallback) {
        this.container = new PIXI.Container()
        this.container.name = 'Robot'
        this.container.interactive = true
        this.data = data
        this.style = {
            fontFamily: 'Arial',
            fontSize: '16px',
            fontWeight: 'bold',
            fill: 0xffffff,
        };

        this.selectCallback = selectCallback

        this.isSelected = false

        this.render()
        this.select()
    }

    render(){
        let data = this.data
        let texture = PIXI.Texture.from('./static/robot.svg');
        this.robotContainer = new PIXI.Sprite(texture);
        this.robotContainer.scale.set(0.4)
        this.robotContainer.anchor.set(0.5)
        this.robotContainer.tint = data.color 
        this.container.addChild(this.robotContainer)

        const textContainer = new PIXI.Text(data.robotId,this.style)
        textContainer.anchor.set(0.5)
        this.container.addChild(textContainer)

        const rotation = this.direction(data.direction)
        this.container.rotation = rotation
        this.container.x = data.locationIndex[0]
        this.container.y = data.locationIndex[1]

        this.lastIndex = null
        this.movedList = {}
    }

    update(value){
        this.container.x = value.locationIndex[0]
        this.container.y = value.locationIndex[1]
        const rotation = this.direction(value.direction)
        this.container.rotation = rotation
        this.data = Object.assign({
            color: this.data.color 
        }, value)

        this.moved(value.nextIndex)
    }

    select() {
        this.container.on("pointerdown", ()=>{
           this.selectCallback && this.selectCallback(this)
        });
    }

    highLight(){
        this.isSelected = !this.isSelected
        if(this.isSelected){
            this.robotContainer.tint = 0xff0000
        }else{
            this.robotContainer.tint = this.data.color
        }
    }

    moved(location){
        if(this.lastIndex && location.toString() == this.lastIndex.toString()) return
        this.lastIndex = location
        this.movedList[location.toString()] ? this.movedList[location.toString()]++ : this.movedList[location.toString()] = 1
    }

    direction(direction){
        let rotation = 0
        switch (direction) {
            case 0:
                rotation = 0.5*Math.PI
                break;
            case 1:
                rotation = 0
                break;
            case 2:
                rotation = 1.5*Math.PI
                break;
            case 3:
                rotation = Math.PI
                break;
        }
        return rotation
    }
}