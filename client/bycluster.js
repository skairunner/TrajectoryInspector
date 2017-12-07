document.addEventListener("DOMContentLoaded", init)

function init() {
	var projection = d3.geoWinkel3(); //geoBaker
	var path = d3.geoPath(projection);
	var color10 = d3.schemeCategory20;
	d3.json("countries.geo.json", (e, d)=>{
		d3.select(".countries")
		  .append("path")
		  .datum(d)
		  .attr("d", path);
		d3.select(".graticules")
		  .append("path")
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
		let clusters = 
			d3.select("#paths")
			  .selectAll(".cluster")
			  .data(d)
			  .enter()
			  .append("g")
			  .classed("cluster", true)
			  .attr("id",d=>"label" + d.label)
			  .datum(d=>d.segments)
			  .selectAll(".segment")
			  .data(d=>d)
			  .enter()
			  .append("path")
			  .classed("segment", true)
			  .each(function(d){
			  	  d3.select(this)
			  	    .classed("icao" + d.icao, true);
			  })
			  .style("stroke", function(d){
			  	  let label = +this.parentNode.getAttribute("id").split("label")[1];
			  	  if (label == -1)
			  	  	  return "#000"
			  	  return color10[label % 10];
			  })
			  .style("stroke-width", function(d){
			  	  let label = this.parentNode.getAttribute("id").split("label")[1];
			  	  return label == -1 ? 0.3 : 0.5;
			  })
			  .attr("d", d=>{
			  	  // repackage data to be GeoJSON
			  	  let geoobj = {type: "LineString", coordinates:[]}
			  	  geoobj.coordinates = d.path.map(el=>[el[0], el[1]])
			  	  return path(geoobj);
			  })
			  .attr("opacity", 0.7);
	})

	let map = d3.select("#map").select(".all");

	let zoom = 
		d3.zoom()
		  .translateExtent([[-100, -100], [1300, 1300]])
		  .on("zoom", function() {
			  	map.attr("transform", d3.event.transform)
			});

	map.append("rect")
	   .attr("x", -800)
	   .attr("y", -800)
	   .attr("width", 1600)
	   .attr("height", 1600)
	   .style("fill", "none")
	   .style("pointer-events", "all")
	   .call(zoom)
}