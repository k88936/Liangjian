export default class Hotmap {
  constructor(opt) {
    this.Container = new PIXI.Container();
    this.hotConfig = opt;
  }
  creatHotInit(data) {
    if (data) {
        if(this.Container){
          this.Container.destroy({
              children: true,
              texture: true,
              baseTexture: true
          })
        }
        this.Container = new PIXI.Container();

        let hotSprite =this.createRadialGradient(data);
        this.Container.addChild(hotSprite);
    }
  }
  clearHotMap(){
    this.Container.destroy({
        children: true,
        texture: true,
        baseTexture: true
    })
  }
  /**
   * 离屏canvas绘制一个黑色的alpha通道的圆
   */
  createRadialGradient(option) {
    const radius = 50;
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = this.hotConfig.width;
    canvas.height = this.hotConfig.height;
    let data = option.data

    data.forEach(point => {
      let { x, y, value } = point;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      // 创建渐变色: r,g,b取值比较自由,关注alpha的数值
      let radialGradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      radialGradient.addColorStop(0, "rgba(0,0,0,1)");
      radialGradient.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = radialGradient;
      ctx.closePath();
      // 设置globalAlpha: 需注意取值需规范在0-1之间
      const max = option.max;
      const min = 0;
      const globalAlpha = (value - min) / (max - min);
      ctx.globalAlpha = Math.max(Math.min(globalAlpha, 1), 0);
      // 填充颜色
      ctx.fill();
    });
    this.colorAlpha(ctx, canvas.width, canvas.height);
    //将canvas画布添加到pixi中
    let texture = PIXI.Texture.from(canvas);
    let hotSprite = new PIXI.Sprite(texture);
    return hotSprite
  }
  createLinearGradient() {
    let canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 256;
    let ctx = canvas.getContext("2d");
    const grd = ctx.createLinearGradient(0, 0, 1, 256);
    const defaultColorStops = {
      0: "#0ff",
      0.2: "#0f0",
      0.5: "#ff0",
      1: "#f00"
    };
    for (const key in defaultColorStops) {
      grd.addColorStop(key, defaultColorStops[key]);
    }
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, 1, 256);
    // 读取像素数据
    this.imageData = ctx.getImageData(0, 0, 1, 256).data;
    return this.imageData;
  }
  // 为alpha通道的圆着色
  colorAlpha(ctx, width, height) {
    const color = this.createLinearGradient();
    const imageData = ctx.getImageData(0, 0, width, height);
    const { data } = imageData;
    for (var i = 3; i < data.length; i += 4) {
      let alpha = data[i];
      if (!alpha * 4) {
        continue;
      }
      if (alpha) {
        data[i - 3] = color[alpha * 4];
        data[i - 2] = color[alpha * 4 + 1];
        data[i - 1] = color[alpha * 4 + 2];
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }
}
