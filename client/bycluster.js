document.addEventListener("DOMContentLoaded", init)

function init() {
	var projection = d3.geoWinkel3(); //geoBaker
	var path = d3.geoPath(projection);
	var color10 = d3.schemeCategory20;
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
		  .datum(d3.geoGraticule())
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
		function getLabel(me) {
			return +me.getAttribute("id").split("label")[1];
		}

		let clusters = 
			d3.select("#paths")
			  .selectAll(".cluster")
			  .data(d)
			  .enter()
			  .append("g")
			  .classed("cluster", true)
			  .attr("id",d=>"label" + d.label)
			  .datum(d=>d.segments)
			  .attr("opacity", .8)
			  .style("stroke", function(d){
			  	  let label = getLabel(this);
			  	  if (label == -1)
			  	  	  return "#000"
			  	  return color10[label % 10];
			  })
			  .style("stroke-width", function(d){
			  	  let label = getLabel(this);
			  	  return label == -1 ? 0.3 : 0.5;
			  })
			  .on("mouseenter", function(d) {
			  	  let label = getLabel(this);
			  	  if (label == -1) return;
			  	  let col = d3.lab(color10[label % 10]);
			  	  d3.select(this)
			  	    .style("stroke", col.darker())
			  	    .style("stroke-width", 1)
			  	    .attr("opacity", 1)
			  	    .raise()
			  })
			  .on("mouseleave", function(d){
			  	  let label = getLabel(this);
			  	  if (label == -1) return;
			  	  d3.select(this)
			  	    .style("stroke", color10[label % 10])
			  	    .attr("opacity", 0.8)
			  	    .style("stroke-width", 0.5);
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