# US Congress

An aggregation of data modeling the United States Congress district boundaries,
including a full history of past districts.

## File format

GeoJSON, in the style of Who's On First records (properties sorted
alphabetically, with the geometry last).

## Directory structure

```
data/[state]/[state]_[start session]_to_[end session]_[district].geojson
```

For example, the 1st congressional district for Idaho, from the 66th to 89th
session is saved at this location:

```
data/id/id_66_to_89_01.geojson
```

## Sources

* [Jeffrey B. Lewis, et al.](https://github.com/JeffreyBLewis/congressional-district-boundaries)  
  Jeffrey B. Lewis, Brandon DeVine, Lincoln Pitcher, and Kenneth C. Martis. (2013) Digital Boundary Definitions of U.S. Congressional Districts, 1789-2012.
* [United States Census TIGER/Line™](https://www.census.gov/geo/maps-data/data/tiger-line.html)
