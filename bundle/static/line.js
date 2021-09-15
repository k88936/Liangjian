import Arrow from './arrow.js'
export default class Line{
    constructor (data,color) {
        this.Container = new PIXI.Graphics()
        this.data = data
        this.color = color
        this.render()
    }
    render(){
        for (let i = 0; i < this.data.length; i++) {
            const [x, y] = this.countXY(this.data[i]);

            this.drawLine([x, y], this.color,i===0)
      
        }
        for (let i = 0; i < this.data.length-1; i++) {
            const [x, y] = this.countXY(this.data[i]);
            const [x1, y1] = this.countXY(this.data[i + 1]);

      
            let propertys = this._countDirProperty([x, y], [x1, y1], false, 0.5)
            for (let i = 0; i < propertys.length; i++) {
              const property = propertys[i]
      
              Arrow(this.Container, property)
            }

        }
    }
    drawLine(start, robotColor, isFirst){
        const [startx,starty] = start;
        this.Container.lineStyle({
            width: 10,
            color: robotColor||'0xCC0000',
            join: 'round',
            cap:'round',
            alpha:0.6
        });
        if(isFirst){
            this.Container.moveTo(startx, starty);
        }else{
            this.Container.lineTo(startx, starty);
        }
        this.Container.zIndex = 2;
    }
    countXY([x,y]){
        const space = 55
        return [x * space,y*space]
    }
    _countDirProperty(point1, point2, isLoad, pos) {
        const [x, y] = point1;
        const [x1, y1] = point2;
        let result = []
        let angle = 0
        angle = (Math.atan2(y1 - y, x1 - x) * 180) / Math.PI - 180
        result.push({
            x: x + (x1 - x) * pos,
            y: y + (y1 - y) * pos,
            angle,
            theta: 45,
            headlen: 5,
            isLoad: isLoad,
        })


        return result
    }
}