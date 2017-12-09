# Trajectory View

This project reads in ADS-B info as downloadable from ADS-B Exchange,
and renders plane trajectories by using the `lat`, `long` and `postime` fields of the data,
applying a trajectory comparison algorithm to produce distances that a clustering algorithm 
consumes for the coloring.

The front-end leverages ES6 features commonly supported by modern browsers, such as fat arrow notation, template literals, class syntax, and for...of notation.
The EDwP algorithm is written in C# for faster speed while still retaining the readability of a high-level language. Visual Studio 2017 will be required to compile the bin.

## Libraries used:
* d3.js
* sklearn
* py-wget
* Selenium
* Newtonsoft Json
* psycopg2
* pillow

## Workflow

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
`icaodbcombiner.py`        | Constructs an `icaodb.json` for frontend to reference.

Utilities           | Description
--------------------|-----------
`combinefiles.py`   | Combines all json files in given directory and outputs as json.


## Works referenced
Contribution | Paper
-------------|-----
EDwP         | S. Ranu et al, *Indexing and Matching Trajectories under Inconsistent Sampling Rates,* 2015 IEEE International Conference on Data Engineering; p999-1010.
Lu & Fu tldr | W. Peng, M. O. Ward, E. A. Rundensteiner; *Clutter Reduction in Multi-Dimensional Data Visualization Using Dimension Reordering*, IEEE Symposium on Information Visualization (2004) ref 15.
Lu & Fu nearest neighbor   | S. Y. Lu and K. S. Fu. *A sentence-to-sentence clustering procedure for pattern analysis,* IEEE Transactions on Systems, Man and Cybernetics, 8:381–389, 1978.
EDR          | L. Chen, M. T. Özsu, V. Oria; *Robust and Fast Similarity Search for Moving Object Trajectories,* SIGMOD/PODS '05.
MA           | S. Sankararaman et al. *Model-driven matching and segmentation of trajectories*, SIGSPATIAL'13; p234-243.
pysklearn    | Pedregosa et al. *Scikit-learn: Machine Learning in Python,* JMLR 12, pp. 2825-2830, 2011.
VW reference | M. Bostock, *simplify.js*, accessed 2017-12-08 [here](bost.ocks.org/mike/simplify/simplify.js) (2012).
VW paper     | M. Visvalingam, J. D. Whyatt. *Line generalisation by repeated elimination of points,* Cartographic Journal 1993, 30, 46–51.
d3           | M. Bostock, V. Ogievetsky, J. Heer. *D3 Data-Driven Documents,* IEEE Transactions on Visualization and Computer Graphics, Volume 17 Issue 12, December 2011. p2301-2309.
Plane info   | ADSBexchange, http://www.ADSBexchange.com.