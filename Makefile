data: \
	sources \
	sessions \
	data_1-112 \
	data_116 \
	simplify \
	data_113_lookup \
	data_113_display \
	data_115_lookup \
	data_115_display \
	assign_ids

sources:
	source_1-112 \
	source_113 \
	source_115 \
	source_pa_116

source_1-112:
	mkdir -p sources/1-112
	curl -o sources/1-112/1-112.zip -L https://github.com/JeffreyBLewis/congressional-district-boundaries/archive/master.zip
	unzip -d sources/1-112 sources/1-112/1-112.zip

source_113: source_113_lookup source_113_display

source_113_lookup:
	mkdir -p sources/113_lookup
	curl -o sources/113_lookup/113_lookup.zip https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d sources/113_lookup sources/113_lookup/113_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/113_lookup/113_lookup.geojson sources/113_lookup/tl_rd13_us_cd113.shp

source_113_display:
	mkdir -p sources/113_display
	curl -o sources/113_display/113_display.zip https://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_cd113_500k.zip
	unzip -d sources/113_display sources/113_display/113_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/113_display/113_display.geojson sources/113_display/cb_2013_us_cd113_500k.shp

source_115: source_115_lookup source_115_display

source_115_lookup:
	mkdir -p sources/115_lookup
	curl -o sources/115_lookup/115_lookup.zip https://www2.census.gov/geo/tiger/TIGER2017/CD/tl_2017_us_cd115.zip
	unzip -d sources/115_lookup sources/115_lookup/115_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/115_lookup/115_lookup.geojson sources/115_lookup/tl_2017_us_cd115.shp

source_115_display:
	mkdir -p sources/115_display
	curl -o sources/115_display/115_display.zip https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_cd115_500k.zip
	unzip -d sources/115_display sources/115_display/115_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/115_display/115_display.geojson sources/115_display/cb_2017_us_cd115_500k.shp

source_pa_116:
	mkdir -p sources/pa_116
	curl -o sources/pa_116/pa_116.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d sources/pa_116 sources/pa_116/pa_116.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 sources/pa_116/pa_116.geojson sources/pa_116/Remedial\ Plan\ Shapefile.shp

sessions:
	python scripts/index_sessions.py

legislators:
	mkdir -p sources/legislators
	curl -o sources/legislators/current.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml
	curl -o sources/legislators/historical.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-historical.yaml
	python scripts/index_legislators.py

data_1-112:
	python scripts/data_1-112.py

data_113: data_113_lookup data_113_display

data_113_lookup:
	python scripts/data_census.py \
		--start=113 \
		--end=115 \
		--type=lookup \
		--exclude=fl,nc,va
	python scripts/data_census.py \
		--start=113 \
		--end=114 \
		--type=lookup \
		--include=fl,nc,va

data_113_display:
	python scripts/data_census.py \
		--start=113 \
		--end=115 \
		--type=display \
		--exclude=fl,nc,va
	python scripts/data_census.py \
		--start=113 \
		--end=114 \
		--type=display \
		--include=fl,nc,va

data_115: data_115_lookup data_115_display

data_115_lookup:
	python scripts/data_census.py \
		--start=115 \
		--end=115 \
		--type=lookup \
		--include=fl,nc,va

data_115_display:
	python scripts/data_census.py \
		--start=115 \
		--end=115 \
		--type=display \
		--include=fl,nc,va

data_pa_116:
	python scripts/data_pa_116.py

assign_ids:
	python scripts/assign_ids.py

simplify:
	python ./scripts/simplify.py

cleanup:
	rm -rf sources/

spatialite:
	python scripts/index_spatialite.py

postgis:
	python scripts/index_postgis.py
