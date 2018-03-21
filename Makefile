all: \
	download_1-112 \
	save_1-112 \
	download_113 \
	save_113 \
	cleanup \
	simplify

download_1-112:
	curl -o congressional-district-boundaries.zip -L https://github.com/JeffreyBLewis/congressional-district-boundaries/archive/master.zip
	unzip congressional-district-boundaries.zip

save_1-112:
	python save_1-112.py

download_113:
	mkdir -p tl_rd13_us_cd113
	curl -O https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d tl_rd13_us_cd113 tl_rd13_us_cd113.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 tl_rd13_us_cd113.geojson tl_rd13_us_cd113/tl_rd13_us_cd113.shp

save_113:
	python save_113.py

cleanup:
	rm congressional-district-boundaries.zip
	rm -rf congressional-district-boundaries-master/
	rm tl_rd13_us_cd113.zip
	rm -rf tl_rd13_us_cd113/
	rm tl_rd13_us_cd113.geojson

simplify:
	./simplify.sh
