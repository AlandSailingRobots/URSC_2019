<template>
  <div class="container">
    <div class="map-info">
      <pre class="pre-wrapper">
        <div>
          <p>Center:</p><code>{{ center.lat }}, {{ center.lng }}</code>
          <p>Zoom:</p><code>{{ zoom }}</code>
        </div>
        <div>
          <p>Bounds:</p><code>{{ bounds }}</code>
        </div>
      </pre>
    </div>
    <div class="map">
      <l-map
        ref="map"
        :zoom="zoom"
        :center="center"
        @update:zoom="zoomUpdated"
        @update:center="centerUpdated"
        @update:bounds="boundsUpdated"
        @click="handleMapClick"
      >
        <l-tile-layer :url="url"></l-tile-layer>
        <l-marker
          v-for="item in markers"
          :key="item.id"
          :lat-lng="item.latlng"
          :draggable="true"
          @drag="handleMarkerDrag($event, item.id)"
        >
          <l-popup>
            <div v-on:click="handleSaveClick">
              <v-btn color="primary" dark class="popup-button">
                Save
                <v-icon dark right>save</v-icon>
              </v-btn>
            </div>
            <div v-on:click="handleDeleteClick($event, item.id)">
              <v-btn color="red" dark class="popup-button">
                Delete
                <v-icon dark right>delete</v-icon>
              </v-btn>
            </div>
            <div v-if="showCyclic(item.id)" v-on:click="handleCyclicClick">
              <v-btn color="green" dark class="popup-button">
                Cyclic
                <v-icon dark right>refresh</v-icon>
              </v-btn>
            </div>
          </l-popup>
        </l-marker>
        <l-polyline ref="polyline" :lat-lngs="polyline.latlngs" :color="polyline.color"></l-polyline>
        <l-polyline v-if="cyclic" ref="polylineCycle" :lat-lngs="polylineCycle.latlngs" :color="polylineCycle.color"></l-polyline>
      </l-map>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import { LMap, LTileLayer, LPolyline, LMarker, LPopup } from "vue2-leaflet";
import FileSaver from "file-saver";

Vue.component("l-map", LMap);
Vue.component("l-tile-layer", LTileLayer);
Vue.component("l-polyline", LPolyline);
Vue.component("l-marker", LMarker);
Vue.component("l-popup", LPopup);

export default {
  data() {
    return {
      url: "https://{s}.tile.osm.org/{z}/{x}/{y}.png",
      zoom: 14,
      center: { lat: 60.098155895160154, lng: 19.964489839048337 },
      bounds: {
        _southWest: {
          lat: 60.080070432727034,
          lng: 19.905252307376422
        },
        _northEast: {
          lat: 60.11545647718221,
          lng: 20.024471133670364
        }
      },
      polyline: {
        uuids: [],
        latlngs: [],
        color: "blue"
      },
      polylineCycle: {
        latlngs: [],
        color: "green"
      },
      markers: [],
      cyclic: false
    };
  },
  methods: {
    zoomUpdated(zoom) {
      this.zoom = zoom;
    },
    centerUpdated(center) {
      this.center = center;
    },
    boundsUpdated(bounds) {
      this.bounds = bounds;
    },
    isFirstMarker(id) {
      return(this.polyline.uuids.indexOf(id) === 0)
    },
    isLastMarker(id) {
      return(this.polyline.uuids.indexOf(id) === this.polyline.uuids.length - 1)
    },
    showCyclic(id) {
      return(this.polyline.uuids.length > 1 && this.isLastMarker(id))
    },
    needUpdateCyclic(id) {
      return(this.polyline.uuids.length > 1 && (this.isFirstMarker(id) || this.isLastMarker(id)))
    },
    updateCyclic() {
      if (this.cyclic) {
        const first = this.polyline.latlngs[0];
        const last = this.polyline.latlngs[this.polyline.latlngs.length - 1];
        Vue.set(this.polylineCycle.latlngs, 0, first);
        Vue.set(this.polylineCycle.latlngs, 1, last);
      }
    },
    handleMapClick(event) {
      const uuid = this.$uuid.v4();
      this.markers.push({
        id: uuid,
        latlng: event.latlng,
        content: "Another"
      });
      this.polyline.uuids.push(uuid);
      this.polyline.latlngs.push(event.latlng);
      this.updateCyclic();
    },
    handleMarkerDrag(event, id) {
      const index = this.polyline.uuids.indexOf(id);
      Vue.set(this.polyline.latlngs, index, event.target._latlng);
      if (this.needUpdateCyclic(id)) {
        this.updateCyclic();
      }
    },
    handleSaveClick() {
      const geoJson = this.$refs.polyline.mapObject.toGeoJSON();
      Vue.set( geoJson['properties'], 'cyclic', this.polyline.uuids.length > 1 && this.cyclic);
      const blob = new Blob(
        [JSON.stringify(geoJson)],
        {
          type: "application/json"
        }
      );
      FileSaver.saveAs(blob, "waypoints.json");
      this.$refs.map.mapObject.closePopup();
    },
    handleDeleteClick(event, id) {
      const needCyclicUpdate = this.needUpdateCyclic(id);
      const index = this.polyline.uuids.indexOf(id);
      this.polyline.latlngs.splice(index, 1);
      this.polyline.uuids.splice(index, 1);
      this.markers.splice(index, 1);
      if (needCyclicUpdate) {
        this.updateCyclic();
      }
    },
    handleCyclicClick() {
      this.cyclic = !this.cyclic;
      this.updateCyclic();
      this.$refs.map.mapObject.closePopup();
    }
  }
};
</script>

<style>
@import "~leaflet/dist/leaflet.css";

.container {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 10% auto 10%;
  grid-template-rows: 300px auto 5%;
}

.map-info {
  grid-column-start: 2;
  grid-row-start: 1;
}

.map {
  grid-column-start: 2;
  grid-row-start: 2;
  width: 100%;
  height: 100%;
}

.icon {
  cursor: pointer;
}
.pre-wrapper {
  display: flex;
  justify-content: space-evenly;
}
.pre-wrapper div {
  flex-grow: 1;
  width: 50%;
}
.pre-wrapper div code {
  width: 80%;
}
.popup-button {
  width: 100%;
}
.v-btn {
  margin: 6px 0;
}
.leaflet-shadow-pane {
  display: none;
}
</style>
