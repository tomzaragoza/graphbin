
/* Load the ArborJS environment */
var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport");

// persistentAddNode(sys, "graph1", "n1", {"x": -3.467437209640285 , "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "200", "fixed": true});
// persistentAddNode(sys, "graph1", "n2", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "100", "fixed": true});
// persistentAddNode(sys, "graph1", "n3", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "300", "fixed": true});
// persistentAddNode(sys, "graph1", "n4", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "350", "fixed": true});
// persistentAddNode(sys, "graph1", "n5", {"x": -1.6054553796477616, "y": -0.318212010897696, "mass": 50, "color": "black", "shape": "dot", "label": "150", "fixed": true});


function persistentAddNode(sys, graphName, nodeName, params) {
	sys.addNode(nodeName, params);

	var newNode = sys.getNode(nodeName);
	params['x'] = newNode.p.x;
	params['y'] = newNode.p.y;
	params['node_name'] = nodeName;
	console.log(params);
	$.ajax({
			type: "POST",
			url: '/store/' + graphName,
			data: params,
			success: function(data) {
				console.log(data);
			}
		});
}

function loadNodes(sys, graphName) {

	$.ajax({
		type: "GET",
		url: "/load/" + graphName,
		success: function(data) {
			var nodes = data.nodes;
			for (var i = 0; i < nodes.length; i++) {
				// console.log(nodes[i]);
				// console.log(nodes[i].node_name);
				sys.addNode(nodes[i].node_name, nodes[i]);
			}
		}
	});
	// console.log("second one");
	// console.log(nodes);
	e.preventDefault();
}

loadNodes(sys, "graph1");
/*
	With the given data, draw out the graph
*/
function graftArbor(sys, data) {
	sys.graft(data);
}

// graftArbor(sys);
