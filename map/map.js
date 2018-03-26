(function() {
	var map = L.map('map').setView([39.715956, -96.999668], 4);
	var layer = Tangram.leafletLayer({
		scene: {
			import: ['/map/refill/refill-style.yaml'],
			global: {
				sdk_api_key: 'vdFEzIDlQwyGrNyZ_MZZuQ'
			}
		}
	}).addTo(map);
	slippymap.crosshairs.init(map);
	var hash = new L.Hash(map);
	L.control.locate({
		setView: 'once',
		drawCircle: false,
		drawMarker: false,
		locateOptions: {
			maxZoom: 17
		}
	}).addTo(map);

	var loading = false;
	var spatialite = document.getElementById('pip-spatialite');
	var postgis = document.getElementById('pip-postgis');
	var status = document.getElementById('status');
	var results = document.getElementById('results');
	var loading_start;
	var district = null;
	var district_layer = null;

	function load_geojson(id) {

		if (! window.XMLHttpRequest) {
			status.innerHTML = 'No XMLHttpRequest object.';
			return;
		}

		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			var DONE = this.DONE || 4;
			if (this.readyState === DONE){
				var geojson = this.responseText;
				var feature = JSON.parse(geojson);
				if (district_layer) {
					district_layer.remove();
				}
				district_layer = L.geoJSON(feature).addTo(map);
			}
		};

		var matches = id.match(/^(\w{2})_/);
		if (! matches) {
			status.innerHTML = 'Could not load ' + id + ' GeoJSON.';
			return;
		}
		var state = matches[1];
		var url = '/data/' + state + '/' + id + '.dp20.geojson';
		xhr.open("GET", url, false);
		xhr.send(null);
	}

	function show_district(id) {
		district = id;
		var selected = document.querySelector('#results li.selected');
		if (selected) {
			selected.className = '';
		}
		var item = document.querySelector('#results li[data-id="' + id +'"]');
		if (item) {
			item.className = 'selected';
		}
		load_geojson(id);
	}

	results.addEventListener('click', function(e) {
		var id = e.target.getAttribute('data-id');
		if (id) {
			show_district(id);
		}
	});

	function show_district_results(districts) {
		var html = '';

		var curr_found = false;
		for (var i = 0; i < districts.length; i++) {
			if (district && districts[i].id == district) {
				curr_found = true;
			}
		}
		if (! curr_found) {
			district = null;
			if (district_layer) {
				district_layer.remove();
				district_layer = null;
			}
			var selected = document.querySelector('#results li.selected');
			if (selected) {
				selected.className = '';
			}
		}

		var auto_select = false;
		for (var i = 0; i < districts.length; i++) {
			if (! district && i == 0) {
				district = districts[i].id;
				selected = ' class="selected"';
				auto_select = true;
			} else if (district && districts[i].id == district) {
				selected = ' class="selected"';
			} else {
				selected = '';
			}
			html += '<li' + selected + ' data-id="' + districts[i].id + '">' + districts[i].id + '</li>';
		}
		html = '<ul>' + html + '</ul>';
		results.innerHTML = html;

		if (auto_select) {
			show_district(district);
		}
	}

	function pip() {

		if (loading) {
			return;
		}

		if (! window.XMLHttpRequest) {
			status.innerHTML = 'No XMLHttpRequest object.';
			return;
		}

		loading = true;
		loading_start = new Date().getTime();
		status.innerHTML = 'Loading...';

		var center = map.getCenter();
		var lat = center.lat;
		var lng = center.lng;
		var endpoint = (spatialite.checked) ? 'spatialite' : 'postgis';
		var url = '/' + endpoint + '?lat=' + lat + '&lng=' + lng;

		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			var DONE = this.DONE || 4;
			if (this.readyState === DONE){
				loading = false;
				var json = xhr.responseText;
				try {
					var rsp = JSON.parse(json);
				} catch(e) {
					status.innerHTML = 'Error loading PIP results.';
					return;
				}

				if (! rsp.results) {
					status.innerHTML = 'Error loading PIP results.';
					return;
				}

				var elapsed_ms = new Date().getTime() - loading_start;
				var elapsed = (elapsed_ms / 1000).toFixed(3) + ' sec';
				var count = rsp.results.length;

				status.innerHTML = 'Found ' + count + ' districts in ' + elapsed;

				show_district_results(rsp.results);
			}
		};
		xhr.open("GET", url, false);
		xhr.send(null);
	}

	map.on('moveend', pip);
	spatialite.addEventListener('change', pip, false);
	postgis.addEventListener('change', pip, false);
})();
