document.addEventListener("DOMContentLoaded", init)

function init() {
	var projection = d3.geoWinkel3(); //geoBaker
	var path = d3.geoPath(projection);
	var color10 = d3.schemeCategory10;
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
	/* d3.json("flightpaths.json", (e, d)=>{
		d = d.slice(0, 10)
		d3.select("#paths")
		  .selectAll("path")
		  .data(d)
		  .enter()
		  .append("path")
		  .attr("stroke", (d,i)=>color10[i])
		  .attr("opacity", 0.7)
		  .attr("id", d=>d.name)
		  .attr("d", d=>path(d.path));
	}); */
	/* d3.json("fullpaths.json", (e, d)=>{
		let getpathtime = d=>d.postime;
		let marginh = 25;
		let width  = 800;
		let height = 150;

		d3.select("#times")
		  .attr("height", height)
		  .attr("width" , width)

		let all = d3.select("#times").select(".all");
		let mintimes = [];
		let maxtimes = [];
		for (let icao in d) {
			let pathinfo = d[icao].path;
			mintimes.push(arrmin(pathinfo, getpathtime));
			maxtimes.push(arrmax(pathinfo, getpathtime));
		}
		let min = arrmin(mintimes, getpathtime);
		let max = arrmax(maxtimes, getpathtime);
		min = getpathtime(min)
		max = getpathtime(max)

		let xscale = 
			d3.scaleLinear()
			  .domain([min, max])
			  .range([0, width]);

		// draw time
		all.select(".elements")
		   .selectAll("g")
		   .data(d)
		   .enter()
		   .append("g")
		   .attr("transform", (d,i)=>`translate(50, ${(i + 5) * 10})`)
		   .attr("icao", d=>d.icao)
		   .attr("fill", (d,i)=>color10[i])
		   .classed("fullpath", true)
		   .selectAll(".timepip")
		   .data(d=>d.path)
		   .enter()
		   .append("circle")
		   .classed("timepip", true)
		   .attr("cx", d=>xscale(getpathtime(d)))
		   .attr("cy", 0)
		   .attr("r", 1);
	});*/

	// draw segments!
	d3.json("segmentedpaths.json", (e, d)=>{
		// Structure of json file:
		/*
			[
				{
					"icao": "ICAO",
					"path": [
						[subpath1]
						[subpath2]
					]
				}
			]
		*/
		d3.select("#paths")
		  .selectAll(".pathgroup")
		  .data(d.map(el=>el.path)) // for each icao
		  .enter()
		  .append("g")
		  .classed("pathgroup", true)
		  .attr("stroke", (d,i)=>color10[i])
		  .selectAll("g")
		  .data(d=>d) // for each subtrajectory
		  .enter()
		  .append("path")
		  .attr("opacity", 0.7)
		  .attr("d", d=>{
		  	// repackage data to be GeoJSON
		  	let geoobj = {type: "LineString", coordinates:[]}
		  	geoobj.coordinates = d.map(el=>[el.long, el.lat])
		  	return path(geoobj);
		  });
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