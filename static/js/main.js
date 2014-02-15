var sys = arbor.ParticleSystem({repulsion: 0, stiffness:1000, friction: 0.5, gravity: false});
sys.parameters({gravity:false});
sys.renderer = Renderer("#viewport") ;
var data = {
	nodes:{
		n1:{'color':'black','shape':'dot','label':'200', 'mass': 50, 'fixed': true},
		n2:{'color':'black','shape':'dot','label':'100', 'mass': 50, 'fixed': true},
		n3:{'color':'black','shape':'dot','label':'300', 'mass': 50, 'fixed': true},
		n4:{'color':'black','shape':'dot','label':'350', 'mass': 50, 'fixed': true},
		n5:{'color':'black','shape':'dot','label':'150', 'mass': 50, 'fixed': true},
	},
	edges:{
		n1:{ n2:{}, n3:{} },
		n2:{ n5:{} },
		n3:{ n4:{} }
	}
};

$("#viewport").mousedown(function(e){
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top}
	nearestNode = sys.nearest(p);

	if (nearestNode.node !== null && nearestNode.distance < 15){
		console.log("===========================");
		console.log("This is the nearest node");
		console.log(nearest.distance);
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
function graftArbor(sys) {
	sys.graft(data);
}

graftArbor(sys);
