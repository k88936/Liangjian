const SimInfo = {
    template: `
        <div class="card mnqInfo">
            <div class="card-header">
            <div class="right">
                <span>当前时间：</span><span class="currentTime">{{simInfo.time || 0}}</span>
            </div>
            <h2>模拟器信息</h2>
            </div>
            <div class="card-body">
            <ul class="setting-item">
                <li class="chooseMap">
                <span>地图选择:</span>
                <select class="select" id="mapSelect" v-model="mapSelect">
                    <option v-for="(option, index) in taskList" :value="index">
                    第 {{ index+1 }} 张
                    </option>
                </select>
                <span class="choose" @click="handlerMapChoose">选择</span>
                </li>
                <li class="chooseMap">
                <span>运行间隔:</span>
                <select class="select selectTime" v-model="inlTime" @change="handleTimeChange">
                    <option v-for="option in inlTimePlace" :value="option">
                    {{ option }} 毫秒
                    </option>
                </select>
                </li>
            </ul>
            <ul class="dataBtn clearfix" id="btns">
                <li class="start" @click="handleStartBtn">{{status=='start'?'暂停':'开始'}}</li>
                <li class="reset" @click="handleResetBtn">重置</li>
            </ul>
            </div>
        </div>
    `,
    props: ['simInfo'],
    data() {
        return {
            status:'stop',
            mapSelect:0,
            inlTime:300,
            inlTimePlace:[0,100,300,500,1000,2000],
            isShowMore:false
        }
    },
    computed: {
        taskList() {
            return new Array(this.simInfo.taskLength || 1).fill(0)
        }
    },
    methods: {
        handleStartBtn(){
            this.status = this.status == 'start' ? 'pause' : 'start'
            this.emitStatusChange()
        },
        handleResetBtn(){
            this.status = 'reset'
            this.emitStatusChange()
        },
        handlerMapChoose(){
            this.status = 'reset'
            this.emitStatusChange()
        },
        handleTimeChange(){
            this.emitStatusChange()
        },
        emitStatusChange(){
            this.$emit('statusChange',{
                status: this.status,
                mapSelect: this.mapSelect,
                inlTime: this.inlTime,
            })
        }
    },
}

export default SimInfo



