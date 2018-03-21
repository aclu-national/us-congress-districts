all: \
	tl_rd13_us_cd113.zip \
	tl_rd13_us_cd113 \
	tl_rd13_us_cd113.geojson \
	113

tl_rd13_us_cd113.zip:
	curl -O https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip

tl_rd13_us_cd113:
	mkdir -p tl_rd13_us_cd113
	unzip -d tl_rd13_us_cd113 tl_rd13_us_cd113.zip

tl_rd13_us_cd113.geojson:
	ogr2ogr -f GeoJSON -t_srs crs:84 tl_rd13_us_cd113.geojson tl_rd13_us_cd113/tl_rd13_us_cd113.shp

113:
	python process_113.py

cleanup:
	rm tl_rd13_us_cd113.zip
	rm -rf tl_rd13_us_cd113/
	rm tl_rd13_us_cd113.geojson
