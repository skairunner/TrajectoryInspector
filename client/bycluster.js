document.addEventListener("DOMContentLoaded", init)

function init() {
	var projection = d3.geoWinkel3(); //geoBaker
	var path = d3.geoPath(projection);
	var color10 = d3.schemeCategory10;
	var graticule =
			d3.geoGraticule()
			  .stepMinor([15, 15]);

	d3.json("countries.geo.json", (e, d)=>{
		d3.select(".countries")
		  .append("path")
		  .attr("id", "countryline")
		  .datum(d)
		  .attr("d", path)
		  .style("stroke-width", 1);
		d3.select(".graticules")
		  .append("path")
		  .attr("id", "graticule")
		  .datum(graticule)
		  .attr("d", path)
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
		console.log(d);
		function getLabel(me) {
			return +me.getAttribute("id").split("label")[1];
		}

		function getColor(me, i) {
			let label = getLabel(me);
			if (label == -1) return d3.lab("#000");
			let metaid = +me.parentNode.getAttribute("metacluster");
			let col = d3.lab(color10[metaid % 10]);
			return col.darker(0.2 * i);
		}

		let clusters = 
			d3.select("#paths")
			  .selectAll(".clustergroup")
			  .data(d)
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
			  .selectAll(".cluster")
			  .data(d=>d)
			  .enter()
			  .append("g")
			  .classed("cluster", true)
			  .attr("id",d=>"label" + d.label)
			  .datum(d=>d.segments)
			  .attr("opacity", .8)
			  .style("stroke", function(d, i){
			  	  return getColor(this, i);
			  })
			  .style("stroke-width", function(d){
			  	  let label = getLabel(this);
			  	  return label == -1 ? 0.3 : 0.5;
			  })
			  .selectAll(".segment")
			  .data(d=>d)
			  .enter()
			  .append("path")
			  .classed("segment", true)
			  .each(function(d){
			  	  d3.select(this)
			  	    .classed("icao" + d.icao, true);
			  })
			  .attr("d", d=>{
			  	  // repackage data to be GeoJSON
			  	  let geoobj = {type: "LineString", coordinates:[]}
			  	  geoobj.coordinates = d.path.map(el=>[el[0], el[1]])
			  	  return path(geoobj);
			  });
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
}