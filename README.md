Trajectory View
===
This project reads in ADS-B info as downloadable from ADS-B Exchange,
and renders plane trajectories by using the `lat`, `long` and `postime` fields of the data,
applying a trajectory comparison algorithm to produce distances that a clustering algorithm 
consumes for the coloring.

Libraries used:
===
d3.js


Workflow
===

Script                     | Description
---------------------------|-----------
`fixjson.py`/`fixjson.py2` | to edit json errors in ADS-B Exchange json files.
`createpostgresql.py`      | to create the postgre tables
`raw2perplane.py`          | converts raw json into postgresql
`samplepaths.py`           | takes given number of paths, output to `data_perplane/`. Also saves icao info in `icao-db/` 
`segmentedpaths.py`        | segments paths from `data_perplane/`
`vw_simplify.py`           | simplifies paths using VW algo, then output to `data_simple-segments/` 
`makemanifest.py`          | Creates a listing of files for use by `dbscan.py` and C# EDwP.
`edwp.exe`                 | Applies EDwP to trajectories to create distance matrix, `distmatrix.json`
`dbscan.py`                | Given a `distmatrix.json`, clusters trajectories into `dbscanned.json`


Utilities           | Description
--------------------|-----------
`createmanifest.py` | Combines all json files in given directory and outputs as json.
