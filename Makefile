data: \
	sources \
	sessions \
	save_1-112 \
	save_113_lookup \
	save_116 \
	simplify \
	save_113_display \
	save_115_display

sources:
	download_1-112 \
	download_113_lookup \
	download_113_display \
	download_115_lookup \
	download_115_display \
	download_116

download_1-112:
	mkdir -p sources/1-112
	curl -o sources/1-112.zip -L https://github.com/JeffreyBLewis/congressional-district-boundaries/archive/master.zip
	unzip -d sources/1-112 sources/1-112.zip

download_113_lookup:
	mkdir -p sources/113-115_lookup
	curl -o sources/113-115_lookup/113-115_lookup.zip https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d sources/113-115_lookup sources/113-115_lookup/113-115_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/113-115_lookup/113-115_lookup.geojson sources/113-115_lookup/tl_rd13_us_cd113.shp

download_113_display:
	mkdir -p sources/113-115_display
	curl -o sources/113-115_display.zip https://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_cd113_500k.zip
	unzip -d sources/113-115_display sources/113-115_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/113-115_display/113-115_display.geojson sources/113-115_display/cb_2013_us_cd113_500k.shp

download_115_lookup:
	mkdir -p sources/115_lookup
	curl -o sources/115_lookup.zip https://www2.census.gov/geo/tiger/TIGER2016/CD/tl_2016_us_cd115.zip
	unzip -d sources/115_lookup sources/115_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/115_lookup/115_lookup.geojson sources/115_lookup/tl_2016_us_cd115.shp

download_115_display:
	mkdir -p sources/115_display
	curl -o sources/115_display.zip https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_cd115_500k.zip
	unzip -d sources/115_display sources/115_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/115_display/115_display.geojson sources/115_display/cb_2017_us_cd115_500k.shp

download_116:
	mkdir -p sources/pa_116
	curl -o sources/pa_116.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d sources/pa_116 sources/pa_116.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/pa_116/pa_116.geojson sources/pa_116/Remedial\ Plan\ Shapefile.shp

sessions:
	python scripts/index_sessions.py

save_1-112:
	python scripts/save_1-112.py

save_115_lookup:
	python scripts/save_census.py \
		--sessions=115 \
		--type=lookup \
		--property=CD115FP \
		--first=115 \
		--last=115 \
		--include=fl,nc,va

save_115_display:
	python scripts/save_census.py \
		--sessions=115 \
		--type=display \
		--property=CD115FP \
		--first=115 \
		--last=115 \
		--include=fl,nc,va

save_116:
	python scripts/save_116.py

simplify:
	python ./scripts/simplify.py

save_113_display:
	python scripts/save_113_display.py

cleanup:
	rm -rf sources/

spatialite:
	python scripts/index_spatialite.py

postgis:
	python scripts/index_postgis.py

datasette_inspect:
	datasette inspect us-congress.db --inspect-file inspect-data.json --load-extension=/usr/local/lib/mod_spatialite.dylib
