export default class RenderShelf{
    constructor (data, selectCallback) {
        this.container = new PIXI.Container()
        this.container.interactive = true
        this.selectCallback = selectCallback
        this.isSelected = false
        this.data = data
        this.container.name = 'SHELF'
        this.render()
        this.select()
    }
    render(){
        let data = this.data
        this.graphics = new PIXI.Graphics()
        this.graphics.beginFill(0xffffff);
        this.graphics.drawPolygon(this.drawShelf());
        this.graphics.endFill();
        this.graphics.tint = 0x4682B4
        this.container.addChild(this.graphics)

        this.container.x = data.placement[0]
        this.container.y = data.placement[1]
    }
    update(data){
        this.container.x =data.placement[0]
        this.container.y =data.placement[1]
        this.data = data
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
        this.container.on("pointerdown", ()=>{
            this.selectCallback(this)
        });
    }

    highLight(){
        this.isSelected = !this.isSelected
        if(this.isSelected){
            this.graphics.tint = 0xff0000
        }else{
            this.graphics.tint = 0x4682B4
        }
    }
}