import {Map, View} from 'ol';
import TileLayer from 'ol/layer/Tile';
//import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';

import TileDebug from 'ol/source/TileDebug';




// For popup
import Overlay from 'ol/Overlay';
//import {toLonLat} from 'ol/proj';
//import {toStringHDMS} from 'ol/coordinate';
/**
 * Elements that make up the popup.
 */
const container = document.getElementById('popup');
const content = document.getElementById('popup-content');
const closer = document.getElementById('popup-closer');

/**
 * Create an overlay to anchor the popup to the map.
 */
const overlay = new Overlay({
  element: container,
  autoPan: true,
  autoPanAnimation: {
    duration: 250,
  },
});

/**
 * Add a click handler to hide the popup.
 * @return {boolean} Don't follow the href.
 */
closer.onclick = function () {
  overlay.setPosition(undefined);
  closer.blur();
  return false;
};



const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new XYZ({
        url:
          //'http://yager-research.ca/Aeyah7gu/tiles/{z}/{x}/{y}.png',
          'http://localhost:2345/maps/MultiMap/tiles/{z}/{x}/{y}.png',
        wrapX: false,
        crossOrigin: 'anonymous',
        cacheSize: 10000,
      }),
      preload: Infinity,
      zIndex: 1,
    }),      
    //new TileLayer({
    //  source: new OSM( {
    //    wrapX: false,    
    //  }),
    //  zIndex: 0,
    //})
    //new TileLayer({
    // source: new TileDebug(),
    // zIndex: 2,
    //}),    
  ],
  overlays: [overlay],
  view: new View({
    center: [0.5, 0.5],
    zoom: 3,
    minZoom: 0,
    maxZoom: 40,
  })
});



/**
 * Add a click handler to the map to render the popup.
 */
map.on('singleclick', function (evt) {
  const coordinate = evt.coordinate;
  //const hdms = toStringHDMS(toLonLat(coordinate));

  content.innerHTML = '<p>You clicked here:</p><code>' + coordinate + '</code><img src="http://localhost:2345/images/AE/anim-grid_vs_autonomous.gif" width="800px"/>';
  overlay.setPosition(coordinate);
});


