import Map from 'ol/Map';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';

const map_sentinel = new Map({
  target: 'map-sentinel',
  layers: [
    new TileLayer({ source: new OSM() }),
    new TileLayer({
      source: new XYZ({
        url: 'http://localhost:3000/media/tiles/ea0ce40b-f2dc-4d6f-aa0e-537943905f51/{z}/{x}/{y}.png',
      }),
    }),
  ],
  view: new View({
    center: map_center,
    zoom: 15,
  }),
});

const map_sat = new Map({
  target: 'map-sentinel',
  layers: [
    new TileLayer({
      source: new XYZ({
        url: 'https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      }),
    }),
  ],
  view: new View({
    center: map_center,
    zoom: 15,
  }),
});

// add event listeners to both maps
map_sentinel.on('moveend', function () {
  // update the zoom level of map1 to be one higher than map2
  map_sat.getView().setZoom(map_sentinel.getView().getZoom() + 1);

  // update the center of map1 to match the center of map2
  map_sat.getView().setCenter(map_sentinel.getView().getCenter());
});

map_sat.on('moveend', function () {
  // update the center of map2 to match the center of map1
  map_sentinel.getView().setZoom(map_sat.getView().getZoom() - 1);
  map_sentinel.getView().setCenter(map_sat.getView().getCenter());
});
