export default function Arrow(container, property = [], fillStyle = {}, lineStyle = {}) {
  if (!property && property.length == 0) return
  const _lineStyle = Object.assign(
    {
      width: 1,
      color: '0xffffff',
    },
    lineStyle,
  )
  const _fillStyle = Object.assign(
    {
      color: '0xffffff',
      alpha: 1,
    },
    fillStyle,
  )
  /**
   *
   * angle [左0,上90,右180,下270 ]
   * headlen 边长度
   * theta 夹角度数
   * isLoad 是否填充
   */
  const _property = Object.assign(
    {
      x: 0,
      y: 0,
      angle: 0,
      theta: 45,
      headlen: 10,
      isLoad: false,
    },
    property,
  )

  // const wrap = container instanceof Graphics ? container : new Graphics()
  let wrap = new PIXI.Graphics()
  if (container instanceof PIXI.Graphics) {
    wrap = container
  } else if (container instanceof PIXI.Container) {
    container.addChild(wrap)
  }

  //   计算角度
  const angle1 = ((_property.angle + _property.theta) * Math.PI) / 180
  const angle2 = ((_property.angle - _property.theta) * Math.PI) / 180
  const topX = _property.headlen * Math.cos(angle1)
  const topY = _property.headlen * Math.sin(angle1)
  const botX = _property.headlen * Math.cos(angle2)
  const botY = _property.headlen * Math.sin(angle2)

  let arrowX, arrowY
  if (_property.isLoad) wrap.beginFill(_fillStyle.color, _fillStyle.alpha)

  wrap.lineStyle(_lineStyle.width, _lineStyle.color)

  wrap.moveTo()
  arrowX = _property.x + topX
  arrowY = _property.y + topY
  wrap.moveTo(arrowX, arrowY)
  wrap.lineTo(_property.x, _property.y)
  arrowX = _property.x + botX
  arrowY = _property.y + botY
  wrap.lineTo(arrowX, arrowY)
  if (_property.isLoad) {
    wrap.endFill()
  }

  return wrap
}
