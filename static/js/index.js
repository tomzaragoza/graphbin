$("#createGraphIndex").click(function(e) {
	console.log("clicked");
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
