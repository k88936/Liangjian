import SimInfo from './sim_info.js'
import EleInfo from './ele_info.js'
import StationInfo from './station_info.js'
import Map from './map.js'
import WS from './ws.js'

const Wrap = {
    data() {
        return {
            mapData:{},
            simInfo:{},
            eleInfo:{},
            stationInfo:null,
            timer:null,
            inlTime:300,
            taskId:0,
            status:'',
            selectEle: null,
            simData: {},
            isShowPath: false,
            isShowHotMap: false,
            isShowResult: false,
            isShowSetting: false,
            extendInfo:null,
            extendSetting: null,
            isNext:false,
        }
    },
    mounted(){
        this.ws = new WS(this.onMessage)
    },
    methods: {
        onMessage(data){
            if(data.type=="init"){
                console.log('data.data: ', data.data);
                this.simInfo.taskLength = data.data.taskLength
                this.extendInfo = data.data.info
                this.extendSetting = data.data.settings
                this.start()
            }
            if(data.type == "start"){
                if(data.code == 1){
                    this.start()
                }else{
                    this.init(data.data)
                }
            }

            if(data.data && data.data.result){
                clearTimeout(this.timer)
                this.simInfo.result = data.data.result
                this.isShowResult = true
                return
            }

            if(data.data && data.data.error){
                clearTimeout(this.timer)
                this.simInfo.result = data.data.result
                this.simInfo.message = data.data.error
                this.isShowResult = true
                return
            }
            
            if(data.type == "next" && data.data){
                this.update(data.data)
                this.next()
            }

        },
        handleStatusChange(value){
            
            const {status, inlTime, mapSelect} = value
            this.taskId = mapSelect
            this.inlTime = inlTime
            this.status = status
            if(status == "start"){
                this.isNext = true
                this.next()
            }

            if(status == 'pause'){
                this.isNext = false
                clearTimeout(this.timer)
            }

            if(status == 'reset'){
                this.isNext = false
                clearTimeout(this.timer)
                this.reset()
                this.start()
            }
        },
        setSimInfo(data){
            const {timestamp, stations} = data
            this.simData = data
            
            this.simInfo.time = timestamp

            this.stationInfo = stations
        },
        init(data){
            this.isNext = false
            this.setSimInfo(data)
            this.$refs.map.init(data)
        },
        update(data){
            this.setSimInfo(data)
            this.$refs.map.update(data);
            this.getSelectInfo()
        },
        start(){
            this.ws.send(JSON.stringify({'step': 'start', 'taskId': this.taskId}));
        },
        next(){
            if(!this.isNext) return
            clearTimeout(this.timer)
            this.timer = setTimeout(()=>{
                this.ws.send(JSON.stringify({'step':'next'})); 
            },this.inlTime);
        },
        reset(){
            this.$refs.map.reset()
        },
        handleEleSelect(type, data){
            this.selectEle = {
                type,
                data:data.data
            }
            this.getSelectInfo()
        },
        getSelectInfo(){
            if(!this.selectEle) return
            this.eleInfo = {}
            if(this.selectEle.type == 'robot'){
                let value = this.selectEle.data.robotId
                let data = this.getItemBySigns("robotId", value, this.simData.robots)
                this.eleInfo = data
            }
            if(this.selectEle.type == 'shelf'){
                let value = this.selectEle.data.code
                let data = this.getItemBySigns("code", value, this.simData.shelves)
                this.eleInfo = data
            }

        },
        getItemBySigns(signs,value, list){
            for (let i = 0; i < list.length; i++) {
                const item = list[i];
                if(item[signs] == value) return item
            }
            return null
        },
        handleExtendSetting(value){
            this.ws.send(JSON.stringify({'step': 'setting', 'event': value, 'taskId': this.taskId}));
        }
    },
    watch: {
        isShowPath(news) {
            this.$refs.map.showPath(news)
        },
        isShowHotMap(news) {
            this.$refs.map.showHotMap(news)
        }
    },
    template: `
        <div>
            <Map ref="map" :mapData="mapData" @ele-select="handleEleSelect" />
            <div class="fixed-bottom button-list">
                <span class="iconfont" :class="{ active: isShowPath }" @click="isShowPath = !isShowPath">&#xe618;</span>
                <span class="iconfont" :class="{ active: isShowHotMap }" @click="isShowHotMap = !isShowHotMap">&#xe640;</span>
                <span class="iconfont" @click="isShowSetting = !isShowSetting">&#xe60b;</span>
                <div class="popover fade show bs-popover-start"
                    :style="{display:isShowSetting?'block':'none'}"
                    style="position: absolute;right: 39px;top:auto;left:auto;width:200px;bottom:0;">
                <div class="popover-arrow" style="position: absolute;bottom:6px;"></div>
                    <h3 class="popover-header">高级设置</h3>
                    <div class="popover-body">
                        <div v-for="setting in extendSetting" class="extend-setting">
                            <div v-if="setting.type=='input'">
                                <span>{{setting.name}}: </span><input type="input" v-model="extendInfo[setting.field]" />
                            </div>
                            <div v-if="setting.type=='button'">
                                <button @click="handleExtendSetting(setting.event)" type="submit" class="btn btn-primary btn-sm">{{setting.name}}</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="slider">
                <sim-info :simInfo="simInfo" @status-change="handleStatusChange" />
                <station-info v-if="stationInfo" :info="stationInfo" />
                <ele-info :eleInfo="eleInfo" />
            </div>
            <div class="modal result_modal" :style="{display:isShowResult?'block':'none'}">
                <div class="modal-dialog modal-sm modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">消息提醒</h5>
                            <button type="button" class="btn-close" @click="isShowResult = false"></button>
                        </div>
                        <div class="modal-body">
                            <p>时间：{{simInfo.time}}</p>
                            <p>成绩：{{simInfo.result}}</p>
                            <p>消息：{{simInfo.message}}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" :style="{display:isShowResult?'block':'none'}"></div>
        </div>
    `,
    components: {
        'sim-info': SimInfo,
        'ele-info': EleInfo,
        'station-info': StationInfo,
        'Map': Map
    }
}

export default Wrap