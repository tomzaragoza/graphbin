$("button.settings").on('click', function() {
	var graphName = $(this).attr('data-graph-name');
	// call on /graph_settings/<graphname>
});

$("button.delete").on('click', function() {
	var graphName = $(this).attr('data-graph-name');
	// call on /delete_graph/<graphname>

	$.ajax({
			type: "GET",
			url: "/delete_graph/" + graphName,
			success: function(data) {
				$("#response-box").html(data);
			}
	});
});