import { createPinia } from 'pinia';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // new router integration
import './index.scss'; // global styles

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');

