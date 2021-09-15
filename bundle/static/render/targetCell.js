export default class EndCell{
    constructor (data,robotColor) {
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
        this.render(robotColor)
    }
    render(robotColor){
        const basicText = new PIXI.Text(this.data.robot_id,this.style)
        basicText.anchor.set(0.5)
        // this.Container.interactive = true;
        this.Container.beginFill(robotColor)
        
        this.Container.drawRect(-this.width/2,-this.width/2, this.width, this.width)
        this.Container.endFill()
        const [x,y] = this.countXY([this.data.destX,this.data.destY])
        this.Container.x = x
        this.Container.y = y
        this.Container.tint = 0xeeeeee
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
    }
    countXY([x,y]){
        const space = 55
        return [x * space, y * space]
    }
}