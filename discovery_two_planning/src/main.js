import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import UUID from 'vue-uuid';
import 'leaflet/dist/leaflet.css'

import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('./assets/baseline-place-24px.svg'),
  iconUrl: require('./assets/baseline-place-24px.svg'),
  shadowUrl: require('./assets/blank.png'),
  iconSize: [40, 40],
  iconAnchor: [19, 36]
});

Vue.config.productionTip = false
Vue.use(UUID)

new Vue({
  render: h => h(App),
}).$mount('#app')
