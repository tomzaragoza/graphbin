
/* Load the ArborJS environment */
var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport");

function backupNodes() {
	persistentAddNode(sys, "graph1", "n1", {"x": -3.467437209640285 , "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "200", "fixed": true});
	persistentAddNode(sys, "graph1", "n2", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "100", "fixed": true});
	persistentAddNode(sys, "graph1", "n3", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "300", "fixed": true});
	persistentAddNode(sys, "graph1", "n4", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "350", "fixed": true});
	persistentAddNode(sys, "graph1", "n5", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "150", "fixed": true});
}

function persistentAddNode(sys, graphName, nodeName, params) {
	sys.addNode(nodeName, params);

	var newNode = sys.getNode(nodeName);
	params['x'] = newNode.p.x;
	params['y'] = newNode.p.y;
	params['node_name'] = nodeName;
	params['type'] = 'node';
	// console.log(params);
	$.ajax({
			type: "POST",
			url: '/store/' + graphName,
			data: params,
			success: function(data) {
				console.log(data);
			}
		});
}

function loadGraph(sys, graphName) {
	/* 
		1) loads nodes
		2) loads corresponding edges
			Note: for 2), check if it automatically loads edges as well
		*/
	$.ajax({
		type: "GET",
		url: "/load/" + graphName,
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

loadGraph(sys, "graph1");
/*
	With the given data, draw out the graph
*/
function graftArbor(sys, data) {
	sys.graft(data);
}

// graftArbor(sys);
