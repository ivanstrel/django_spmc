import 'ol/ol.css';
import Map from 'ol/Map';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import { Fill, Stroke, Style } from 'ol/style';
import View from 'ol/View';
import OSM from 'ol/source/OSM';
import BingMaps from 'ol/source/BingMaps';
import XYZ from 'ol/source/XYZ';
import Vector from 'ol/source/Vector';
import * as d3 from 'd3';
import GeoJSON from 'ol/format/GeoJSON';
import Select from 'ol/interaction/Select';
import { click } from 'ol/events/condition';
import { getCenter } from 'ol/extent';

function hexToRgba(hex, alpha) {
  let r = parseInt(hex.substring(1, 3), 16);
  let g = parseInt(hex.substring(3, 5), 16);
  let b = parseInt(hex.substring(5, 7), 16);
  return [r, g, b, alpha];
}

// List of geojson's to geojson
function list2geojson(list) {
  return {
    type: 'FeatureCollection',
    srid: 3857,
    features: list.map((segment) => ({
      type: 'Feature',
      geometry: JSON.parse(segment.features),
      properties: {
        id: segment.id,
        land_class_id: segment.land_class_id,
        color: segment.color,
      },
    })),
  };
}

/**
 * Prepare miscellaneous layers =====================================================================================
 */
// Create array of miscellaneous layers
let misc_layers = Object.getOwnPropertyNames(misc_tiles).map((key) => {
  return new TileLayer({
    name: misc_tiles[key].name,
    visible: false,
    source: new XYZ({
      url: misc_tiles[key].path,
    }),
  });
});

// Create array of layers names on `map_sentinel`
let sentinel_layers_names = Object.getOwnPropertyNames(misc_tiles).map(
  (key) => {
    return misc_tiles[key].name;
  },
);
sentinel_layers_names = ['SentinelRGB'].concat(sentinel_layers_names);

// Generate array of key codes allowed for layer selection
let allowed_layer_digits = [];
for (let i = 0; i < sentinel_layers_names.length; i++) {
  allowed_layer_digits.push('Digit' + (i + 1));
  allowed_layer_digits.push('Numpad' + (i + 1));
}
/**
 * Initiate maps ====================================================================================================
 */
const map_sentinel = new Map({
  target: 'map-sentinel',
  layers: [
    new TileLayer({ name: 'OSM', source: new OSM() }),
    new TileLayer({
      name: 'SentinelRGB',
      source: new XYZ({
        url: 'http://localhost:3000/media/tiles/ea0ce40b-f2dc-4d6f-aa0e-537943905f51/{z}/{x}/{y}.png',
      }),
    }),
  ].concat(misc_layers),
  view: new View({
    center: map_center,
    zoom: 15,
  }),
});

const map_sat = new Map({
  target: 'map-sentinel',
  layers: [
    new TileLayer({
      name: 'ESRI',
      source: new XYZ({
        url: 'https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      }),
    }),
    new TileLayer({
      name: 'Bing',
      visible: false,
      preload: Infinity,
      source: new BingMaps({
        key: 'Asy2HQTzPXirXy5Ro2GCPGoR7dVNveFIhXM7QdmyYRo2prQNw-2M1c32Vg1NwC0Q',
        imagerySet: 'Aerial',
        maxZoom: 19,
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

/**
 * Map layers handlers ==============================================================================================
 */
// Get the layer by its name
function getLayerByName(map, name) {
  let layers = map.getLayers().getArray();
  for (var i = 0; i < layers.length; i++) {
    if (layers[i].get('name') === name) {
      return layers[i];
    }
  }
  return null;
}

// Change the visibility of a layer by name
function setLayerVisibilityByName(map, name, visibility) {
  let layer = getLayerByName(map, name);
  if (layer) {
    layer.setVisible(visibility);
  }
}

/**
 * Selection handlers ================================================================================================
 */
// Create a new select interaction with multi selection enabled
let selectInteraction = new Select({
  condition: click,
  multi: false,
});

// When a feature is selected, update its style
selectInteraction.on('select', function (event) {
  // Update selected features style
  event.selected.forEach(function (feature) {
    feature.setStyle(
      new Style({
        fill: new Fill({
          color: feature.get('color')
            ? hexToRgba(feature.get('color'), 0.2)
            : 'rgba(255, 255, 255, 0)',
        }),
        stroke: new Stroke({
          color: 'rgba(255, 255, 255, 1)',
          width: 1,
        }),
        zIndex: 100,
      }),
    );
  });
  // Center map on selected feature
  let ext = event.selected.slice(-1)[0].getGeometry().getExtent();
  let cntr = getCenter(ext);
  map_sat.getView().setCenter(cntr);
});

/**
 * Class assignment handlers =========================================================================================
 */
function send_update(obj) {
  fetch(api_upd_url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf_token,
    },
    body: JSON.stringify({ upd: obj }),
  })
    .then((response) => response.json())
    // TODO ad handling of responses
    .then((result) => {
      console.log('Server response:', result);
      // Handle the response from the server
    })
    .catch((error) => {
      console.error('Error:', error);
      // Handle any errors that occurred during the request
    });
}

function assign_class(id, color) {
  // Get currently selected features
  let cur_selected = selectInteraction.getFeatures();
  if (cur_selected.get('length') === 0) {
    return null;
  }

  // Prepare an object for POST request
  let server_update_obj = [];

  cur_selected.forEach(function (feature) {
    feature.set('land_class_id', id);
    feature.set('color', color);
    server_update_obj.push({
      superpixel_id: feature.get('id'),
      class_id: id,
      scene_id: scene_id,
    });
  });
  // Send update request to server
  send_update(server_update_obj);
  // Clear selection
  selectInteraction.getFeatures().clear();
}
// Make the function global
window.assign_class = assign_class;
// On num keyboard press, update the class property for currently selected feature
document.addEventListener('keydown', function (event) {
  // Prepare accepted events codes
  let event_codes = class_col.flatMap((segment) => [
    'Numpad' + segment.key,
    'Digit' + segment.key,
  ]);
  // Convert class_col into JSON based on key value
  let class_col_obj = {};
  for (const item of class_col) {
    const { key, ...rest } = item;
    class_col_obj[key] = rest;
  }
  // First check that event key was from accepted keys (i.e. accepted num-key for classes)
  if (event_codes.indexOf(event.code) > -1 && !event.altKey && !event.ctrlKey) {
    // Get class object
    let cur_land_class = class_col_obj[event.key];
    // Assign class and color to selected features
    assign_class(cur_land_class.land_class_id_id, cur_land_class.color);
  } else {
    // If ctrl+9 set ESRI base layer if ctrl+0 set Bind layer
    if (
      (event.code === 'Digit0' || event.code === 'Numpad0') &&
      event.ctrlKey
    ) {
      setLayerVisibilityByName(map_sat, 'Bing', true);
      setLayerVisibilityByName(map_sat, 'ESRI', false);
    }
    if (
      (event.code === 'Digit9' || event.code === 'Numpad9') &&
      event.ctrlKey
    ) {
      setLayerVisibilityByName(map_sat, 'Bing', false);
      setLayerVisibilityByName(map_sat, 'ESRI', true);
    }
    // If ctrl+1:ctrl+8 set appropriate layer visibility
    if (allowed_layer_digits.indexOf(event.code) > -1 && event.ctrlKey) {
      // Get target layer name basing on event key
      let cur_layer_name = sentinel_layers_names[event.key - 1];
      // Change layer visibility (except OSM and Vector)
      map_sentinel.getLayers().forEach(function (layer) {
        if (layer.get('name') === cur_layer_name) {
          setLayerVisibilityByName(map_sentinel, cur_layer_name, true);
        } else {
          if (layer.get('name') !== 'OSM' && layer.get('name') !== 'Vector') {
            setLayerVisibilityByName(map_sentinel, layer.get('name'), false);
          }
        }
      });
    }
  }
});

/**
 * Add vector map =====================================================================================================
 */
d3.json('/api/superpixels/get_sp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf_token },
  body: JSON.stringify({
    srid: 3857,
    scene_id: scene_id,
    algo_id: algo_id,
  }),
}).then(function (data) {
  // Construct geojson
  let geojson = list2geojson(data);
  // Create a new layer to display the GeoJSON data
  const vectorLayer = new VectorLayer({
    name: 'Vector',
    source: new Vector({
      features: new GeoJSON().readFeatures(geojson),
    }),
    style: function (feature, resolution) {
      return new Style({
        stroke: new Stroke({
          color: feature.get('color'),
          width: 1,
        }),
        fill: new Fill({
          // Set feature fill as transparent if color property is null or use a property color
          color: feature.get('color')
            ? hexToRgba(feature.get('color'), 0.5)
            : [0, 0, 0, 0],
        }),
      });
    },
  });

  // Add the vector layer to the map
  map_sat.addLayer(vectorLayer);
  map_sentinel.addLayer(vectorLayer);

  // Add the select interaction to the map
  map_sentinel.addInteraction(selectInteraction);
});
