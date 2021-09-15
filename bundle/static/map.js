import Render from './render/render.js'

const Map = {
    props: ['mapData'],
    data() {
        return {
            offsetWidth: 0,
            offsetHeight: 0,
        }
    },
    template: `
        <div ref="map" class="map">
        </div>
    `,
    mounted() {
        this.create()
    },
    methods: {
        init(data){
            this.render.render(data)
            this.viewport.fitWorld()
            this.viewport.x = (this.offsetWidth - this.viewport.width) / 2 + 50*this.viewport.scaled / 2
            this.viewport.y = (this.offsetHeight - this.viewport.height) / 2 + 50*this.viewport.scaled / 2
        },
        reset(){
            this.render.reset()
        },
        update(data){
            this.render.update(data)
        },
        create(){
            let mapDom = this.$refs.map
            this.offsetHeight = mapDom.offsetHeight
            this.offsetWidth = mapDom.offsetWidth
            let App = new PIXI.Application({
                width: mapDom.offsetWidth,
                height: mapDom.offsetHeight,
                antialias: true,
                autoDensity: true,
            })
            App.ticker.maxFPS = 20
            this.viewport = new Viewport.Viewport({
                screenWidth: mapDom.offsetWidth,
                screenHeight: mapDom.offsetHeight,
                passiveWheel: false,
                divWheel: mapDom,
                interaction: App.renderer.plugins.interaction,
            })
            App.renderer.backgroundColor = 0xf2f2f2
            App.stage.addChild(this.viewport)
            this.viewport.drag().pinch().wheel({
                percent: 0.01,
            })
            this.viewport.sortableChildren = true
            mapDom.appendChild(App.view)
    
    
            this.render = new Render(this.viewport, this.selectCallback)
        },
        selectCallback(type, data){
            this.$emit('ele-select', type, data)
        },
        showPath(bol){
            this.render.showPath(bol)
        },
        showHotMap(bol){
            this.render.showHotMap(bol)
        }
    },
}

export default Map



