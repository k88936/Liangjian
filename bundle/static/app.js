import Wrap from './wrap.js'
const app = Vue.createApp({
    template: `
        <wrap />
    `,
    components: {
        'wrap': Wrap,
    }
})


app.mount('#app')