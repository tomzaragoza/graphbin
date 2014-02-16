/*
	This will be the dragging function
*/
$("#viewport").mousedown(function(e){
	// Will need graphname
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);
	console.log(nearestNode);
	if (nearestNode.node !== null && nearestNode.distance < 15){
		var params = {
						'node_name': nearestNode.node.name,
						'x': nearestNode.node.p.x,
						'y': nearestNode.node.p.y
				};
		console.log("MOUSEDOWN");
		console.log(params.x);
		console.log(params.y);
	}
	e.preventDefault();
});

$("#viewport").mouseup(function(e) {
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);
	
	if (nearestNode.node !== null){
			var params = {
							'label': nearestNode.node.data.label,
							'color': nearestNode.node.data.color,
							'shape': nearestNode.node.data.shape,
							'node_name': nearestNode.node.name,
							'type': 'node',
							'x': nearestNode.node.p.x,
							'y': nearestNode.node.p.y
					};
			console.log("MOUSEUP");
			console.log(params.x);
			console.log(params.y);
			$.ajax({
					type: "POST",
					url: "/store/graph1",
					data: params,
					success: function(data) {
						console.log(data);
					}
			});
		}
		e.preventDefault();
});

$("#newNode").click(function(e) {
	console.log("new node!");
	// Get nodes from database
	// insert the node information into the database
	// If attaching the node to another node, must re-render the entire graph

	// else if a node on it's own, just add it like so:
	sys.addNode("n<COUNT>", {"mass": 50, "color": "black", "shape": "dot", "label": "XYZ", "fixed": true});
});


$("#addEdge").click(function(e) {
	var n_source = sys.getNode('n1');
	var n_target = sys.getNode('n2');
	
	sys.addEdge(n_source, n_target); // Don't need to specify length.
	var params = {
					'source': 'n1',
					'target': 'n2',
					'name': 'n1 to n2',
					'type': 'edge'
		};
	$.ajax({
			type: "POST",
			url: "/store/graph1",
			data: params,
			success: function(data) {
				console.log(data);
			}
	});
	e.preventDefault();
	// console.log(sys.getEdgesFrom(n_source));
});