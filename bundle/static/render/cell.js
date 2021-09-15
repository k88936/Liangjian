export default class Cell{
    constructor () {
        // this.Container = new PIXI.ParticleContainer()
        // this.Container.interactive = true

        // this.data = data
        // this.selectedCell = selectedCell
        
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
            'BLOCKED_CELL': '0xcccccc',
        }
    }
    render(data){
        const Container = new PIXI.Container()
        Container.interactive = true;

        const bg = new PIXI.Graphics()
        bg.beginFill(this.CELL_COLOR[data.cellType]||'0xD2E5F5')
        bg.drawRect(-this.width/2,-this.width/2, this.width, this.width)
        bg.endFill()
        Container.addChild(bg)

        return Container
    }
    renderText(data){
        const Container = new PIXI.Container()
        Container.interactive = true;

        const bg = new PIXI.Graphics()
        bg.beginFill(robotColor||this.CELL_COLOR[data.cellType]||'0xD2E5F5')
        bg.drawRect(-this.width/2,-this.width/2, this.width, this.width)
        bg.endFill()
        Container.addChild(bg)
        
        const basicText = new PIXI.Text(data.robot_id,this.style)
        basicText.anchor.set(0.5)
        Container.addChild(basicText)

        switch (data.endDirection) {
            case 0:
                Container.rotation = 0.5*Math.PI
                break;
            case 1:
                Container.rotation = 0
                break;
            case 2:
                Container.rotation = 1.5*Math.PI
                break;
            case 3:
                Container.rotation = Math.PI
                break;
        }
        
        return Container

    }
}