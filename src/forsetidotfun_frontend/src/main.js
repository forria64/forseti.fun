import { createPinia } from 'pinia';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './index.scss';
import actor from './Agent.js'; // import the actor here

const app = createApp(App);

// Provide the actor globally so components can inject it
app.provide('actor', actor);

app.use(createPinia());
app.use(router);
app.mount('#app');

