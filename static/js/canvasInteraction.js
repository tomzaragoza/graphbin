var select_s = false;
var select_t = false;
var select_delete = false;
var select_e = false;
var isEditing = false;

// use this to grab the graph name being loaded
var pathname = window.location.pathname.split('/');
var graphname = pathname[pathname.length -1];

$("#graphname-header").html(graphname);

/*
	The Graph mouse operations
*/
$("#viewport").mousedown(function(e){
	// Will need graphname
	var pos = $(this).offset();
	var p = {x:e.pageX-pos.left, y:e.pageY-pos.top};
	nearestNode = sys.nearest(p);

	if (nearestNode.node !== null && nearestNode.distance < 15){

		if (select_s === true) {
			$("#source").html(nearestNode.node.name);
		}

		if (select_t === true) {
			$("#target").html(nearestNode.node.name);
		}

		if (select_e === true) {
			isEditing = true;
			$("#node-label").val(nearestNode.node.data.label);
			$("#node-name").val(nearestNode.node.name);
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

		if (select_delete === true) {
			select_delete = false;
			if (confirm("delete?")) {
				var nodeNameToDelete = sys.getNode(nearestNode.node.name);
				
				sys.pruneNode(nodeNameToDelete);
				var params = {
								'node_name': nearestNode.node.name,
								'edges_to_delete': edgesToDelete.toString()
					};

				$.ajax({
					type:"POST",
					url: "/delete_node/" + graphname,
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
				url: "/store/" + graphname,
				data: params,
				success: function(data) {
				}
		});
		}
		e.preventDefault();
});

/*
	The Graph keydown operations
*/
$("#viewport").keydown(function(e){

	if(e.keyCode == 83){
		select_s = true;
	} else if(e.keyCode == 84){
		select_t = true;
	} else if (e.keyCode == 68) {
		select_delete = true;
	} else if (e.keyCode == 69) {
		select_e = true;
	}
	e.preventDefault();
});

$("#viewport").keyup(function (e) {
	select_s = false;
	select_t = false;
	select_delete = false;
	select_e = false;

});


$("#clearNodes").click(function() {
	$("#viewport").focus();
	$("#source").empty();
	$("#target").empty();
});

$("#exportGraph").click(function() {
	var canvas = document.getElementById("viewport");
	var ctx = canvas.getContext("2d");

	// draw to canvas...
	canvas.toBlob(function(blob) {
		saveAs(blob, graphname + ".png");
	});
});


/*
	Node selection for adding edges
*/

$(document).click(function(e) {
	// To return to blue button and unfocus
	// when clicking anywhere on the document.
	var graphDistance = $(e.target).closest('#viewport').length;
	var selectionModeDistance = $(e.target).closest('#selectionMode').length;
    if (graphDistance === 0 && selectionModeDistance === 0) {
        selectionToBlue();
    }
});

function stringGen(len)
{
    var text = " ";

    var charset = "abcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < len; i++ )
        text += charset.charAt(Math.floor(Math.random() * charset.length));

    return text;
}

var graphFocus = function () {
	$("#viewport").attr("tabindex", "0");
	$("#viewport").focus();
};

function selectionToRed() {
	$("#selectionMode").removeClass("btn-primary")
				.addClass("btn-danger")
				.html("Done selecting");
	graphFocus();
}

function selectionToBlue() {
	$("#selectionMode").removeClass("btn-danger")
			.addClass("btn-primary")
			.html("Selection mode");
}

$("#selectionMode").click(function(e) {
	if ($("#selectionMode").attr("class").indexOf("btn-primary") !== -1) {
		// contains btn-primary
		selectionToRed();
	} else {
		selectionToBlue();
	}
});


$("#addOrEditNode").click(function(e) {
	var nodeLabel = $("#node-label").val();
	var nodeName = $("#node-name").val();
	var canCreateNode = false;

	if (nodeName === '') {
		nodeName = stringGen(13);
	} 

	if (nodeLabel === '') {
		alert("Incorrect node label: must not be empty");
	} else {
		canCreateNode = true; // passed the two tests above
	}

	if (canCreateNode) {
		$("#node-label").val('');
		$("#node-name").val('');
		var xCoord = -6.0;
		var yCoord = -7.0;

		var data = {
						"mass": 50,
						"color": "black",
						"shape": "dot",
						"label": nodeLabel,
						"fixed": true
					};

		if (!isEditing) {
			data['x'] = xCoord;
			data['y'] = yCoord;
		}

		var newNode = sys.addNode(nodeName, data);
		// Until i figure out how to get points from node
		var params = {
						'label': nodeLabel,
						'color': "black",
						'shape': "dot",
						'node_name': nodeName,
						'type': 'node',
					};

		if (!isEditing) {
			params['x'] = xCoord;
			params['y'] = yCoord;
		}

		isEditing = false;

		$.ajax({
				type: "POST",
				url: "/store/" + graphname,
				data: params,
				success: function(d) {
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
						'edge_name': n_source_name + ' to ' + n_target_name,
						'type': 'edge'
			};
		$.ajax({
				type: "POST",
				url: "/store/" + graphname,
				data: params,
				success: function(d) {
					$("#source").empty();
					$("#target").empty();
				}
		});
		e.preventDefault();
	} else {
		alert("Please select two appropriate nodes to add an edge to.");
		selectionToRed();
	}
});


$("#deleteEdge").click(function(e) {
	console.log("deleteEdge clicked");
	var n_source_name = $("#source").html();
	var n_target_name = $("#target").html();

	if (n_source_name.length > 0 && n_target_name.length > 0 ) {
		var n_source = sys.getNode(n_source_name);
		var n_target = sys.getNode(n_target_name);

		var params = {
						'source': n_source_name,
						'target': n_target_name,
						'edge_name': n_source_name + ' to ' + n_target_name,
						'type': 'edge'
			};
		$.ajax({
				type: "POST",
				url: "/delete_edge/" + graphname,
				data: params,
				success: function(data) {
					$("#source").empty();
					$("#target").empty();

					if (data.deleted) {
						var allEdges = sys.getEdges(n_source, n_target).concat(sys.getEdges(n_target, n_source));
						for  (var i = 0; i < allEdges.length; i++) {
							sys.pruneEdge(allEdges[i]);
						}
					}
				}
		});
		e.preventDefault();
	} else {
		alert("Please select two nodes to delete an edge from.");
		selectionToRed();
	}
});