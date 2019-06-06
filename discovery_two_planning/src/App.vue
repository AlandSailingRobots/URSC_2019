<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>{{ title }}</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn flat v-bind:href="src" target="_blank">
        <span class="mr-2">Source</span>
      </v-btn>
    </v-toolbar>

    <v-content>
      <Leaflet/>
    </v-content>
  </v-app>
</template>

<script>
import Leaflet from "./components/Leaflet.vue";

export default {
  name: "App",
  components: {
    Leaflet
  },
  data() {
    return {
      title: "sailboat-planing-vue",
      src: "https://github.com/D3473R/sailboat-planing-vue"
    };
  }
};
</script>