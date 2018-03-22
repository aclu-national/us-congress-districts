# US Congress District Shapes

An aggregation of data modeling the United States Congress district boundaries,
including a full history of past districts.

## File format

[GeoJSON](http://geojson.org/), in the style of [Who's On First](https://whosonfirst.org/)
records (pretty-printed, properties sorted alphabetically, with the geometry
last). Note that records lack a Who's On First numeric ID; these records have
not been imported into the Who's On First gazetteer (yet), I am just using
the WOF encoding style.

## File paths

The directory structure and filename are constructed using the following:

* 2-char state (e.g., `ca` for California, or `dc` for District of Columbia,
  from Python's [`us` package](https://pypi.python.org/pypi/us))
* When the district started, by congressional session
* When the district ended, by congressional session
* District number (0 refers to at-large, -1 is for "shapes describing Indian
  territories within states during the 18th and early 19th centuries," from
  [Lewis, et al.](https://github.com/JeffreyBLewis/congressional-district-boundaries#documentation))

```
data/[state]/[state]_[start session]_to_[end session]_[district].geojson
```

For example, the 1st congressional district for Idaho, from the 66th to 89th
session is saved at this location:

```
data/id/id_66_to_89_01.geojson
```

## Simplified geometries

There are also simplified versions of the geometries. For geometries run through
Mapshaper with Douglas-Peucker 20% simplification, add `.dp20` to the filename:

```
data/id/id_66_to_89_01.dp20.geojson
```

## Building from scratch

You can rebuild the data from the original sources, by using `make`.

## Spatialite index

You can build a SQLite/Spatialite index with: `make index`.

## Dependencies

* `make`, `curl`, `unzip`
* [Python 2.7](https://www.python.org/)
	- [us](https://pypi.python.org/pypi/us)
	- [py-mapzen-whosonfirst-sources](http://github.com/whosonfirst/py-mapzen-whosonfirst-sources)
	- [py-mapzen-whosonfirst-geojson](http://github.com/whosonfirst/py-mapzen-whosonfirst-geojson)
	- [py-mapzen-whosonfirst-utils](http://github.com/whosonfirst/py-mapzen-whosonfirst-utils)
* [GDAL](http://gdal.org/)
* [Mapshaper](https://github.com/mbloch/mapshaper)
* [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/index)

## Sources

* [Jeffrey B. Lewis, et al.](https://github.com/JeffreyBLewis/congressional-district-boundaries)  
  Jeffrey B. Lewis, Brandon DeVine, Lincoln Pitcher, and Kenneth C. Martis. (2013) Digital Boundary Definitions of U.S. Congressional Districts, 1789-2012.
* [United States Census TIGER/Line®](https://www.census.gov/geo/maps-data/data/tiger-line.html)
