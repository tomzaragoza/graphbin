var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport");

persistentAddNode(sys, "n1", {"mass": 50, "color": "black", "shape": "dot", "label": "200", "fixed": true});
persistentAddNode(sys, "n2", {"mass": 50, "color": "black", "shape": "dot", "label": "100", "fixed": true});
persistentAddNode(sys, "n3", {"mass": 50, "color": "black", "shape": "dot", "label": "300", "fixed": true});
persistentAddNode(sys, "n4", {"mass": 50, "color": "black", "shape": "dot", "label": "350", "fixed": true});
persistentAddNode(sys, "n5", {"mass": 50, "color": "black", "shape": "dot", "label": "150", "fixed": true});


function persistentAddNode(sys, nodeName, params) {
	sys.addNode(nodeName, params);
	// Store the x and y coordinates and pass that in to params
	console.log(params);
	$.ajax({
			type: "POST",
			url: '/store',
			data: params,
			success: function(data) {
				console.log(data);
			}
		});
}

$("#viewport").mousedown(function(e){
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);

	if (nearestNode.node !== null && nearestNode.distance < 15){
		console.log("===========================");
		console.log("This is the nearest node");
		console.log(nearestNode.distance);
		console.log(nearestNode.node);
		console.log("x coordinates of nearestNode node");
		console.log(nearestNode.node.p.x);
		console.log("y coordinates of nearestNode node");
		console.log(nearestNode.node.p.y);
		nearestNode.node.fixed = true;
	}
	return false;
});

$("#newNode").click(function(e) {
	console.log("new node!");
	// Get nodes from database
	// insert the node information into the database
	// If attaching the node to another node, must re-render the entire graph

	// else if a node on it's own, just add it like so:
	sys.addNode("n<COUNT>", {"mass": 50, "color": "black", "shape": "dot", "label": "XYZ", "fixed": true});
});

/*
	With the given data, draw out the graph
*/
function graftArbor(sys, data) {
	sys.graft(data);
}

// graftArbor(sys);
