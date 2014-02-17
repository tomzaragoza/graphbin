var shift_f = false;
var shift_t = false;
var shift_delete = false;

$("#viewport").mousedown(function(e){
	// Will need graphname
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);
	// console.log(nearestNode);
	if (nearestNode.node !== null && nearestNode.distance < 15){

		if (shift_f === true) {
			$("#source").html(nearestNode.node.name);
		}

		if (shift_t === true) {
			$("#target").html(nearestNode.node.name);
		}

		if (shift_delete === true) {
			alert("delete?");
		}
		var params = {
						'node_name': nearestNode.node.name,
						'x': nearestNode.node.p.x,
						'y': nearestNode.node.p.y
				};
		// console.log("MOUSEDOWN");
		// console.log(params.x);
		// console.log(params.y);
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
			// console.log("MOUSEUP");
			// console.log(params.x);
			// console.log(params.y);
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


/*
	Node selection for adding edges
*/
$(document).keydown(function(e){

	if(e.shiftKey && e.keyCode == 70){
		shift_f = true;
	} else if(e.shiftKey && e.keyCode == 84){
		shift_t = true;
	} else if (e.shiftKey && e.keyCode == 68) {
		shift_delete = true;
	}
	e.preventDefault();
});

$(document).keyup(function (e) {
	shift_f = false;
	shift_t = false;
	shift_delete = false;
});

$("#newNode").click(function(e) {
	console.log("new node!");
	// Get nodes from database
	// insert the node information into the database
	// If attaching the node to another node, must re-render the entire graph

	// else if a node on it's own, just add it like so:
	sys.addNode("n9999", {"mass": 50, "color": "black", "shape": "dot", "label": "XYZ", "fixed": true});
});


$("#addEdge").click(function(e) {

	var n_source_name = $("#source").html();
	var n_target_name = $("#target").html();

	if (n_source_name.length > 0 && n_target_name.length > 0 ) {
		var n_source = sys.getNode(n_source_name);
		var n_target = sys.getNode(n_target_name);
		
		sys.addEdge(n_source, n_target); // Don't need to specify length.
		var params = {
						'source': n_source_name,
						'target': n_target_name,
						'name': n_source_name + ' to ' + n_target_name,
						'type': 'edge'
			};
		$.ajax({
				type: "POST",
				url: "/store/graph1",
				data: params,
				success: function(data) {
					console.log(data);
					$("#source").empty();
					$("#target").empty();
				}
		});
		e.preventDefault();
	} else {
		alert("Please select two appropriate nodes to add an edge to.");
	}
});