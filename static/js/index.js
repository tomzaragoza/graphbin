$("#createGraphIndex").click(function(e) {
	$("#loading").html("<p>Creating an empty graph. You'll be redirected to it...</p>");
	$.ajax({
				type: "POST",
				url: "/nonregistered_create_graph",
				success: function(d) {
					if (d.created) {
						console.log("success");
						console.log(d.url);

						window.location = "http://localhost:5000/graph_nonregistered/" + d.url;
					} else if (d.created === false) {
						window.location = "http://localhost:5000/";
					}
				},
				error: function(e) {
					console.log("error");
				}

	});
});
