var shift_f = false;
var shift_t = false;
var shift_delete = false;

$("#viewport").mousedown(function(e){
	// Will need graphname
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);
	// console.log(nearestNode.point);
	if (nearestNode.node !== null && nearestNode.distance < 15){

		if (shift_f === true) {
			$("#source").html(nearestNode.node.name);
		}

		if (shift_t === true) {
			$("#target").html(nearestNode.node.name);
		}

		var edgesFrom = sys.getEdgesFrom(nearestNode.node);
		var edgesTo = sys.getEdgesTo(nearestNode.node);

		var edgesToDelete = [];
		for (var i = 0; i < edgesFrom.length; i++) {
			var edgeFromInDB = edgesFrom[i].source.name + ' to ' + edgesFrom[i].target.name;
			edgesToDelete.push(edgeFromInDB);
		}

		for (var j = 0; j < edgesTo.length; j++) {
			var edgeToInDB = edgesTo[j].source.name + ' to ' + edgesTo[j].target.name;
			edgesToDelete.push(edgeToInDB);
		}

		if (shift_delete === true) {
			shift_delete = false;
			if (confirm("delete?")) {
				var nodeNameToDelete = sys.getNode(nearestNode.node.name);
				
				sys.pruneNode(nodeNameToDelete);
				var params = {
								'node_name': nearestNode.node.name,
								'edges_to_delete': edgesToDelete.toString()
					};

				$.ajax({
					type:"POST",
					url: "/delete/graph1",
					data: params,
					success: function(data) {
						console.log("sucessfully deleted");
					}
				});
				e.preventDefault();
			} else {
				console.log("do not delete the node");
			}
		}
		e.preventDefault();
	}
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
$("#selectionMode").click(function(e) {
	if ($(this).attr("class").indexOf("btn-primary") !== -1) { // contains
		$(this).removeClass("btn-primary")
				.addClass("btn-danger")
				.html("Done selecting");
	} else {
		$(this).removeClass("btn-danger")
				.addClass("btn-primary")
				.html("Selection mode");
		$(document).focus();
	}
	$("#viewport").attr("tabindex", "0");
	$("#viewport").focus();
});

$("#viewport").keydown(function(e){
	console.log("keydown on viewport");
	if(e.shiftKey && e.keyCode == 70){
		shift_f = true;
	} else if(e.shiftKey && e.keyCode == 84){
		shift_t = true;
	} else if (e.shiftKey && e.keyCode == 68) {
		shift_delete = true;
	}
	e.preventDefault();
});

$("#viewport").keyup(function (e) {
	shift_f = false;
	shift_t = false;
	shift_delete = false;
});

$("#addNode").click(function(e) {

	var nodeLabel = $("#node-label").val();
	var nodeName = $("#node-name").val();
	var canCreateNode = false;

	if (nodeName === '' || ~nodeName.indexOf(',')) {
		alert("Incorrect node name: must not contain commas or be empty");
		// if the same name as another node, it will update it.
	} else if (nodeLabel === '') {
		alert("Incorrect node label: must not be empty");
	} else {
		canCreateNode = true; // passed the two tests above
	}

	if (canCreateNode) {
		$("#node-label").val('');
		$("#node-name").val('');
		var xCoord = -6.0;
		var yCoord = -8.0;
		var data = {	
						"x": xCoord,
						"y": yCoord,
						"mass": 50,
						"color": "black",
						"shape": "dot",
						"label": nodeLabel,
						"fixed": true
					};
		var newNode = sys.addNode(nodeName, data);
		// Until i figure out how to get points from node
		var params = {
						'label': nodeLabel,
						'color': "black",
						'shape': "dot",
						'node_name': nodeName,
						'type': 'node',
						'x': xCoord,
						'y': yCoord
					};
		$.ajax({
				type: "POST",
				url: "/store/graph1",
				data: params,
				success: function(data) {
					console.log(data);
				}
		});
	}
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