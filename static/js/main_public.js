// use this to grab the graph name being loaded
var pathname = window.location.pathname.split('/');
var publicUrl = pathname[pathname.length -1];
console.log(publicUrl);

/* Load the ArborJS environment */
var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport");

function loadGraph(sys, graphName) {
	/* 
		1) loads nodes
		2) loads corresponding edges
			Note: for 2), check if it automatically loads edges as well
		*/
	$.ajax({
		type: "GET",
		url: "/public_load/" + publicUrl,
		success: function(data) {
			// Load the nodes in their place
			var nodes = data.nodes;
			// console.log(nodes);
			for (var i = 0; i < nodes.length; i++) {
				sys.addNode(nodes[i].node_name, nodes[i]);
			}

			// Load the edges in their place
			var edges = data.edges;
			// console.log(edges);
			for (var j = 0; j < edges.length; j++) {
				sys.addEdge(edges[j].source, edges[j].target);
			}
			return false;
		}
	});
}

loadGraph(sys, publicUrl);
/*
	With the given data, draw out the graph
*/
function graftArbor(sys, data) {
	sys.graft(data);
}

// graftArbor(sys);
