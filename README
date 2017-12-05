Libraries used:
	d3.js


Workflow

`fixjson.py` / `fixjson2.py` to edit json errors in ADS-B Exchange json files.
`createpostgresql.py`        to create the tables
`raw2perplane.py`            converts raw json into postgresql
`samplepaths.py`             takes given number of paths, output to `data_perplane/`
                             also saves icao info in `icao-db/`
`segmentedpaths.py`          segments paths from `data_perplane/`
                             and outputs to `data_segmented-paths/`
`vw_simplify.py`             takes all paths in `data_segmented-paths/`
                             simplifies paths using VW algo, then output
                             to `data_simple-segments/`
