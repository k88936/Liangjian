export default class Cell{
    constructor (data, selectedCell) {
        this.Container = new PIXI.Graphics()
        this.data = data
        this.selectedCell = selectedCell
        
        this.Container.name = 'EndCell'
        this.Container.interactive = true
        this.width = 50
        this.style = {
            fontFamily: 'Arial',
            fontSize: '20px',
            fontWeight: 'bold',
            fill: '#fff',
            align: 'center'
        }; 
        this.CELL_COLOR = {
            'QUEUE_CELL': '0xEDE2BE',
            'STATION_CELL': '0xF29361',
            'TURN_CELL': '0xD7C99F',
            'OMNI_DIR_CELL': '0xD2E5F5',
            'SHELF_CELL': '0x8BD4DB',
            'BLOCKED_CELL': '0xcccccc'
        }
        this.render()
    }
    render(robotColor){
        const basicText = new PIXI.Text(this.data.robot_id,this.style)
        basicText.anchor.set(0.5)
        // this.Container.interactive = true;
        this.Container.beginFill(robotColor||this.CELL_COLOR[this.data.cellType]||'0xD2E5F5')
        
        this.Container.drawRect(-this.width/2,-this.width/2, this.width, this.width)
        this.Container.endFill()
        const [x,y] = this.countXY(this.data.index)
        this.Container.x = x
        this.Container.y = y
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
        // viewport.addChild(this.Container)
        this.event()
    }
    event(){
        this.Container.on("pointerdown", ()=>{
            console.log(this.data)
            if(this.data.cellType == "QUEUE_CELL" || this.data.cellType == "TURN_CELL" || this.data.cellType == "STATION_CELL"){
                this.selectedCell(this.data)
            }
        });
    }
    countXY([x,y]){
        const space = 55
        return [x * space,y*space]
    }
}