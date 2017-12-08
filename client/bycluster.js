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

	// first element is type, second is data
	var filter = {type: null, how: null};
	var filtercss = {
		icao: {
			fillcol: "#8e0000",
			fontcol: "#FFFFFF",
			name: "ICAO"
		},
		operator: {
			fillcol: "#4c4cff",
			fontcol: "#FFFFFF",
			name: "operator"
		},
		country: {
			fillcol: "#0b280b",
			fontcol: "#FFFFFF",
			name: "country"
		},
		meta: {
			fillcol: "#8727db",
			fontcol: "#FFFFFF",
			name: "cluster"
		},
		other: {
			fillcol: "#AAAAAA",
			fontcol: "#FFFFFF",
			name: "Show all"
		}
	}

	function setfilter(type, how) {
		filter.type = type;
		filter.how  = how;

		let fillcol, fontcol, text;
		if (type in filtercss) {
			let f = filtercss[type];
			fillcol = f.fillcol;
			fontcol = f.fontcol;
			text    = f.name;
		} else {
			let f = filtercss.other;
			fillcol = f.fillcol;
			fontcol = f.fontcol;
			text    = f.name;
		}
		d3.select("#filter")
		  .transition()
		  .duration(300)
		  .styleTween("background-color", function(d){
		  	  return d3.interpolateLab(d3.select(this).style("background-color"),
		  	  			fillcol);
		  })
		  .style("color", fontcol);

		d3.select(".filtertype")
		  .text(text);
		update();
	}
	d3.select("#filter")
	  .on("click", ()=>setfilter(null, null));
	d3.select("#clear")
	  .on("click", ()=>setfilter(null, null));


	// returns true if should display normally, false otherwise.
	function checkfilter(icao, meta) {
		if (filter.type == null)
			return true;
		if (filter.type == "icao")
			return icao == filter.how;
		if (filter.type == "operator")
			return icaodb[icao].operator == filter.how;
		if (filter.type == "country")
			return icaodb[icao].country == filter.how;
		if (filter.type == "meta")
			return meta == filter.how;
		return true;
	}

	function getstrokewidth(me, mouseovered) {
		let icao = me.getAttribute("icao");
		let meta = +me.parentNode.parentNode.getAttribute("metacluster")
		let label = getLabel(me);
		if (label == -1)
			return 0.3;
		if (mouseovered) {
			return 1.15;
		} else if (checkfilter(icao, meta)) {
			return 0.9;
		} else {
			return 0.2;
		}
	}

	function getopacity(me, mouseovered) {
		if (mouseovered)
			return 1;
		let icao = me.getAttribute("icao");
		let meta = +me.parentNode.parentNode.getAttribute("metacluster")
		let label = getLabel(me);

		if (checkfilter(icao, meta)) {
			return 0.9;
		} else {
			return 0.2;
		}
	}

	function maketable(me) {
		let metaid = +me.getAttribute("metacluster");
		setfilter("meta", metaid);
		// set color bar
		d3.select("#colorbar")
		  .transition()
		  .duration(300)
		  .styleTween("background-color", function(d){
		  	  return d3.interpolateLab(d3.select(this).style("background-color"),
		  	  			color10[metaid % 10]);
		  })

		let icaos = new Set();
		d3.select(me)
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
			.classed("filterable", true)
			.text(d=>icaodb[d].icao)
			.on("click", d=>setfilter("icao", d));
		rows.append("td")
			.classed("country", true)
			.classed("filterable", true)
			.on("click", d=>setfilter("country", icaodb[d].country))
			.text(d=>icaodb[d].country);
		rows.append("td")
			.classed("logo", true)
			.classed("filterable", true)
			.on("click", d=>setfilter("operator", icaodb[d].operator))
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
			.classed("filterable", true)
			.on("click", d=>setfilter("operator", icaodb[d].operator))
			.text(d=>icaodb[d].operator);
		rows.append("td")
			.classed("model", true)
			.text(d=>icaodb[d].model);
	}

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

    function setup() {
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
			  	  .selectAll(".segment")
			  	  .each(function(d,i) {
					  	let col = getColor(this);
					  	d3.select(this)
					  	  .style("stroke", col.darker())
					  	  .style("stroke-width", getstrokewidth(this, true))
					  	  .attr("opacity", getopacity(this, true));
			  	    });
			})
			.on("mouseleave", function(d, i){
				if (i == 0) return; // metagroup0 is the outliers
				d3.select(this)
				  .selectAll(".segment")
				  .each(function(d, i) {
					let col = getColor(this);
					  	d3.select(this)
					  	  .transition()
					  	  .duration(300)
					  	  .style("stroke", col)
					  	  .style("stroke-width", getstrokewidth(this))
					  	  .attr("opacity", getopacity(this));
				    });
			})
			.on("click", function(d) {
				if (icaodb == null)
					return;
				maketable(this);

			})
			.merge(metaclusters);

		let clusters = metaclusters
			.selectAll(".cluster")
			.data(d=>d);
		// ENTER clusters
		clusters = clusters
			.enter()
			.append("g")
			.classed("cluster", true)
			.attr("id",d=>"label" + d.label)
			.attr("n", (d,i)=>i)
			.datum(d=>d.segments)
			.merge(clusters);
		
		// ENTER segments
		let segments = clusters
			.selectAll(".segment")
			.data(d=>d)
			.enter()
			.append("path")
			.classed("segment", true)
			.each(function(d){
				  d3.select(this)
				    .attr("icao", d.icao);
			})
			.style("stroke", function(d, i){
				return getColor(this);
			})
			.style("stroke-width", function(d){
				return getstrokewidth(this);
			})
			.attr("d", "")
    }

    function update() {
    	let clusters = d3
    		.selectAll(".cluster");;

		let segments = d3
			.selectAll(".segment")
			.transition()
			.duration(300)
			.style("stroke", function(d, i){
				return getColor(this);
			})
			.style("stroke-width", function(d){ return getstrokewidth(this); })
			.style("opacity", function(d){ return getopacity(this); })
			.attr("d", d=>{
				  // repackage data to be GeoJSON
				  let geoobj = {type: "LineString", coordinates:[]}
				  geoobj.coordinates = d.path.map(el=>[el[0], el[1]])
				  return path(geoobj);
			});
    }

	// get the label from an element
	function getLabel(me) {
		return +me.parentNode.getAttribute("id").split("label")[1];
	}

	// get the right color for a trajectory
	function getColor(me) {
		let label = getLabel(me);
		if (label == -1) return d3.lab("#000");
		let metaid = +me.parentNode.parentNode.getAttribute("metacluster");
		let col = d3.lab(color10[metaid % 10]);
		let n = +me.parentNode.getAttribute("n");
		return col.darker(0.2 * n);
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

		setup();
		update();
		setfilter(null, null);
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

	MAGICNUM = 1200;
    function resizesvg() {
    	let W = window.innerWidth;
    	let w = W * .50;
    	if (W < MAGICNUM)
    		w = W * .9;
    	d3.select("svg")
    	  .transition()
    	  .duration(300)
    	  .attr("width", w);

    	// also resize table width
    	if (W < MAGICNUM)
    		d3.select("table").style("width", "80vw")
    	else
    		d3.select("table").style("width", "40vw");

    }
    resizesvg();
	d3.select(window)
	  .on("resize", resizesvg);
}