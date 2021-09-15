const EleInfo = {
    template: `
        <div class="card info">
        <div class="card-header">
            <h2>元素信息</h2>
        </div>
        <div class="card-body infoBody">
            <p v-for="(value, name) in eleInfo">{{name}}: {{value}}</p>
        </div>
        </div>
    </div>
    `,
    props: ['eleInfo'],
}

export default EleInfo



