"use strict";

document.addEventListener("DOMContentLoaded", init)

var UPDATE;

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

	//draw annotated segments
	d3.json("../dbscanned.json", (e, d)=>{
		// Structure of json file:
		/*
			[
				{
					"icao": "ICAO",
					"label": #,
					"rep": #,
					"path": [
						[subpath1]
					]
				},
			]
		*/
		// fix the start and ends of each path
		var clusters = {};
		// each cluster will have such structure
		/*
			.nodes = [<nodes in node format>]
			.links    = [<links in link format>]
			.force    = d3.forceSimulation
			.attract  = d3.forceManyBody
			.link     = d3.forceLink
		*/
		function getDefaultCluster(dict, key) {
			if (!(key in dict)) {
				dict[key] = {nodes:[], links:[]};
			}
			return dict[key];
		}

		var forcesim;
		var linkforce, attraction;
		function setup() {
			// create force sims per cluster
			for (var seg of d) {
				let cluster = getDefaultCluster(clusters, seg.label);
				seg.nodepath = [];
				for (var node of seg.path) {
					seg.nodepath.push({
						x: node[0],
						y: node[1]
					});
					var seg0 = seg.nodepath[0]
					seg0.fx = seg0.x;
					seg0.fy = seg0.y;
					let L = seg.nodepath.length;
					var seg9 = seg.nodepath[L - 1];
					seg9.fx = seg9.x;
					seg9.fy = seg9.y;
					for (let i = 0; i < L; i++) {
						cluster.nodes.push(seg.nodepath[i]);
						if (i != L - 1) {
							cluster.links.push({source: seg.nodepath[i], target:seg.nodepath[i+1]});
						}
					}
				}
			}

			for (var label in clusters) {
				let cluster = clusters[label];
				cluster.force   = d3.forceSimulation(cluster.nodes);
				cluster.link    = d3.forceLink(cluster.links);
				cluster.attract = d3.forceManyBody()
									.strength(10);
	 			cluster.force
	 			    .force("link", cluster.link)
	 			    .force("attract", cluster.attract)
	 			    .on("end", update);
			}

			d3.select("#paths")
			  .selectAll("path")
			  .data(d)
			  .enter()
			  .append("path")
			  .attr("stroke", (d,i)=>d.label == -1 ? "#00F" : color10[d.label])
			  .attr('stroke-width', d=>d.rep ? 0.3 : 0.3)
			  .attr("opacity", 0.7);

			update();
		}

		function update() {
			console.log("update");
			d3.select("#paths")
			  .selectAll("path")
			  .data(d)
			  .attr("d", d=>{
			  	// repackage data to be GeoJSON
			  	let geoobj = {type: "LineString", coordinates:[]}
			  	geoobj.coordinates = d.nodepath.map(el=>[el.x, el.y]);
			  	return path(geoobj);
			  });
		}
		UPDATE = update;
		setup();
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