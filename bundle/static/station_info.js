const StationInfo = {
    template: `
        <div class="card info">
            <div class="card-header">
                <div class="right">
                    <select class="select" id="mapSelect" v-model="curStation">
                        <option v-for="(value, index) in info" :value="value.id">
                        {{ value.id }} 号工作站
                        </option>
                    </select>
                </div>
                <h2>工作站信息</h2>
            </div>
            <div class="card-body infoBody">
                <p v-for="(value, name) in curInfo">{{name}}: {{value}}</p>
            </div>
        </div>`,
    props: ['info'],
    data() {
        return {
            curStation:this.info && this.info[0].id || 0,
        }
    },
    computed: {
        curInfo() {
            for (let i = 0; i < this.info.length; i++) {
                const item = this.info[i];
                if(this.curStation == item.id) return item
            }
            return {}
        }
    }
}

export default StationInfo



