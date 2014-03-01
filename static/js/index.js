$("#createGraphIndex").click(function(e) {
	$(this).attr("disabled", true);
	$(this).html("Redirecting...");
	$("#loading").html("<br><img src='/static/img/loadingrays.gif' alt='loading...'></img>");
	$.ajax({
				type: "POST",
				url: "/nonregistered_create_graph",
				success: function(d) {
					if (d.created) {
						window.location = "https://graphbin.co/graph_nonregistered/" + d.url;
					} else if (d.created === false) {
						window.location = "https://graphbin.co/";
					}
				},
				error: function(e) {
					console.log("error");
				}

	});
});
