document.addEventListener("DOMContentLoaded", init)

function init() {
	var projection = d3.geoWinkel3(); //geoBaker

	// LARK ZONE
	var projid = 0;
	var projections = [
		d3.geoWinkel3(),
		d3.geoBaker(),
		d3.geoAzimuthalEquidistant(),
		d3.geoConicEquidistant()];
	var projnames = [
		"winkel3",
		"baker",
		"azimuthal equidistant",
		"conic equidistant"
	];
	var countryshapes, pathinfo, icaodb = null;

	//

	var path = d3.geoPath(projection);
	var color10 = d3.schemeCategory10;
	var graticule =
			d3.geoGraticule()
			  .stepMinor([15, 15]);

    function drawCountries() {
		d3.select(".countries")
		  .html("")
		  .append("path")
		  .attr("id", "countryline")
		  .datum(countryshapes)
		  .attr("d", path)
		  .style("stroke-width", 1);
		d3.select(".graticules")
		  .html("")
		  .append("path")
		  .attr("id", "graticule")
		  .datum(graticule)
		  .attr("d", path)
    }

    function setupandupdate() {
    	let metaclusters = d3
    		.select("#paths")
    		.html("")
			.selectAll(".clustergroup")
			.data(pathinfo);
		// ENTER megaclusters
		metaclusters = metaclusters
			.enter()
			.append("g")
			.classed("clustergroup", true)
			.attr("metacluster", (d,i)=>i)
			.on("mouseenter", function(d, i){
				if (i == 0) return; // metagroup0 is the outliers
			 	d3.select(this)
			  	  .raise()
			  	  .selectAll(".cluster")
			  	  .each(function(d,i) {
					  	let col = getColor(this, i);
					  	d3.select(this)
					  	  .style("stroke", col.darker())
					  	  .style("stroke-width", 1)
					  	  .attr("opacity", 1);
			  	    });
			})
			.on("mouseleave", function(d, i){
				if (i == 0) return; // metagroup0 is the outliers
				d3.select(this)
				  .selectAll(".cluster")
				  .each(function(d, i) {
					let col = getColor(this, i);
				  	d3.select(this)
				  	  .transition()
				  	  .duration(300)
				  	  .style("stroke", col)
				  	  .style("stroke-width", 0.5)
				  	  .attr("opacity", .8);
				    });
			})
			.on("click", function(d) {
				if (icaodb == null)
					return;
				let icaos = new Set();
				d3.select(this)
				  .selectAll(".segment")
				  .each(d=>icaos.add(d.icao));
				icaoarr = []
				for (let icao of icaos)
					icaoarr.push(icao)
				// sort array by airline
				icaoarr.sort((a, b)=>{
					a = icaodb[a].operator;
					b = icaodb[b].operator;
					if (a > b) return  1;
					if (a < b) return -1;
					return 0;
				})
				let sel = d3
					.select("#planes")
					.selectAll("tr")
					.data(icaoarr, d=>d);
				sel.exit().remove();
				let rows = sel
					.enter()
				    .append("tr");
				rows.append("td")
					.classed("icao", true)
					.text(d=>icaodb[d].icao)
				rows.append("td")
					.classed("icao", true)
					.text(d=>icaodb[d].country)
				rows.append("td")
					.classed("logo", true)
					.append("img")
					.attr("src", d=>{
						let url = icaodb[d].operator;
						url = url.toLowerCase().replace(/ /g, "-");
						return `logos/${url}.png`;
					})
					.attr("width", 100)
					.attr("alt", d=>icaodb[d].operator);
				rows.append("td")
					.classed("operator", true)
					.text(d=>icaodb[d].operator);
				rows.append("td")
					.classed("model", true)
					.text(d=>icaodb[d].model);

			})
			.merge(metaclusters);
		// no UPDATE for metaclusters

		let clusters = metaclusters
			.selectAll(".cluster")
			.data(d=>d);
		// ENTER clusters
		clusters = clusters
			.enter()
			.append("g")
			.classed("cluster", true)
			.attr("id",d=>"label" + d.label)
			.datum(d=>d.segments)
			.merge(clusters);
		// UPDATE clusters
		clusters
			.attr("opacity", .8)
			.style("stroke", function(d, i){
				return getColor(this, i);
			})
			.style("stroke-width", function(d){
				let label = getLabel(this);
				return label == -1 ? 0.3 : 0.5;
			});
		
		// ENTER segments
		let segments = clusters
			.selectAll(".segment")
			.data(d=>d);

		segments = segments
			.enter()
			.append("path")
			.classed("segment", true)
			.each(function(d){
				  d3.select(this)
				    .attr("icao", d.icao);
			})
			.merge(segments)
		// UPDATE segments
		segments
			.attr("d", d=>{
				  // repackage data to be GeoJSON
				  let geoobj = {type: "LineString", coordinates:[]}
				  geoobj.coordinates = d.path.map(el=>[el[0], el[1]])
				  return path(geoobj);
			});
    }

    function populatetable() {

    }

	// get the label from an element
	function getLabel(me) {
		return +me.getAttribute("id").split("label")[1];
	}

	// get the right color for a trajectory
	function getColor(me, i) {
		let label = getLabel(me);
		if (label == -1) return d3.lab("#000");
		let metaid = +me.parentNode.getAttribute("metacluster");
		let col = d3.lab(color10[metaid % 10]);
		return col.darker(0.2 * i);
	}

	d3.json("countries.geo.json", (e, d)=>{
		countryshapes = d;
		drawCountries();
	});

	d3.json("icaodb.json", (e, d)=>{
		icaodb = d;
	});

	//draw annotated clusters
	d3.json("../dbscanned.json", (e, d)=>{
		// Structure of json file:
		/*
			{
				<label>: {
					"label": <label>,
					"segments": [
						{
							"path": [<coords>],
							"icao": <icao>
						},
						...
					]
				}
			}
		*/
		pathinfo = d;

		setupandupdate();
	})

	let map = d3.select("#map").select(".all");

	// adaptive zooming
	class AdaptiveZoomState {
		constructor(zoomlevels, strokewidths) {
			this.zoomstate = {zoom: 0, oldzoom: 0};
			this.zoomlevels = zoomlevels;
			this.strokewidths = strokewidths;
		}

		setzoom(k, selector) {
			let zs = this.zoomstate;
			for (let i = 0; i < this.zoomlevels.length; i++) {
				if (k < this.zoomlevels[i]) {
					zs.zoom = i;
					break;
				}
			}
			if (zs.zoom != zs.oldzoom) {
				d3.select(selector)
				  .transition()
				  .duration(300)
				  .style("stroke-width", this.strokewidths[zs.zoom]);
				zs.oldzoom = zs.zoom;
			}
		}
	}

	let countryzoom =
		new AdaptiveZoomState(
				[0, 3, 5, 10],
				[1.0, 0.7, 0.3, 0.15]);
	let graticulezoom =
		new AdaptiveZoomState(
				[0, 5, 10],
				[1.0, 0.7, 0.5]);

	let zoom = 
		d3.zoom()
		  .translateExtent([[-100, -100], [1300, 1300]])
		  .on("zoom", function() {
		  		let k = d3.event.transform.k;
		  		countryzoom.setzoom(k, "#countryline");
		  		graticulezoom.setzoom(k, "#graticule")
			  	map.attr("transform", d3.event.transform)
			});

	map.insert("rect", ":first-child")
	   .attr("x", -800)
	   .attr("y", -800)
	   .attr("width", 3200)
	   .attr("height", 2400)
	   .style("fill", "none")
	   .style("pointer-events", "all")
	   .call(zoom)

	// create projection buttons
	d3.select("#buttons")
	  .selectAll("button")
	  .data(projections)
	  .enter()
	  .append("button")
	  .text((d,i)=>projnames[i])
	  .on("click", (d, i)=>{
	  		path = d3.geoPath(d);
	  	    setupandupdate();
	  	    drawCountries();
	  });

    function resizesvg() {
    	let W = window.innerWidth;
    	let w = W * .50;
    	if (W < 1281)
    		w = W * .9;
    	d3.select("svg")
    	  .transition()
    	  .duration(300)
    	  .attr("width", w);
    }
    resizesvg();
	d3.select(window)
	  .on("resize", resizesvg);
}