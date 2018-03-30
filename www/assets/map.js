(function() {
	var map = L.map('map').setView([39.715956, -96.999668], 4);
	var layer = Tangram.leafletLayer({
		scene: {
			import: ['/assets/refill/refill-style.yaml'],
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
	var status = document.getElementById('status');
	var results = document.getElementById('results');
	var loading_start;
	var district = null;
	var district_layer = null;
	var district_results = null;

	function show_geojson(id) {
		try {
			var geom = JSON.parse(district_results[id]);
			var feature = {
				type: "Feature",
				properties: {},
				geometry: geom
			};
		} catch(e) {
			console.error('Could not show GeoJSON for ' + id);
			return;
		}
		if (district_layer) {
			district_layer.remove();
		}
		district_layer = L.geoJSON(feature).addTo(map);
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
		show_geojson(id);
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
		var url = '/pip?lat=' + lat + '&lng=' + lng;

		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function() {
			var DONE = this.DONE || 4;
			if (this.readyState === DONE){
				loading = false;
				var json = xhr.responseText;
				try {
					var rsp = JSON.parse(json);
					district_results = {};
					var id, geom;
					for (var i = 0; i < rsp.results.length; i++) {
						id = rsp.results[i].id;
						geom = rsp.results[i].boundary_simple;
						district_results[id] = geom;
					}
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
	pip();
})();
