export default class RenderShelf{
    constructor (data, selectedShelf) {
        this.Container = new PIXI.Graphics()
        this.targetContainer = new PIXI.Graphics()
        this.data = data
        this.Container.name = 'SHELF'
        this.selected = ""
        this.selectedShelf = selectedShelf
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
        this.Container.beginFill(0x4682B4);
        this.Container.drawPolygon(this.drawShelf());
        this.Container.endFill();
        this.Container.interactive = true;

        const [x,y] = this.countXY(this.data.placement)
        this.Container.x = x
        this.Container.y = y
        this.Container.zIndex = 5;

        this.select(this.data.code)
    }
    renderTarget(){
        let width = 50
        this.targetContainer.zIndex = 3;
        this.targetContainer.alpha = 0;

        const {targetArea} = this.data

        this.targetContainer.beginFill(0xff4444)
        for (let i = 0; i < targetArea.length; i++) {
            const {x,y} = targetArea[i];
            const [drawX,drawY] = this.countXY([x,y])
            this.targetContainer.drawRect(drawX-width/2,drawY-width/2, width, width)
        }
        this.targetContainer.endFill();
    }
    update(value){
        const [x,y] = value.placement
        this.Container.x = x
        this.Container.y = y
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
            this.selectedShelf(this)
        });
    }
    highLight(code){
        let highlightArr =  messageList.ShelfList[code].data.assignedPath
        for(let i = 0; i < highlightArr.length-1; i++){
            let item = highlightArr[i].code
             messageList.ShelfList[item].tint = 0xde553f
        }
    }
    countXY([x,y]){
        const space = 55
        return [x * space,y*space]
    }
}