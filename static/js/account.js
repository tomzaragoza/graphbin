function loadGraphList() {
	$.ajax({
		type: "POST",
		url: "/load_graph_list",
		success: function(data) {
			$("#graphList").html(data);
		}
	});
}

$(document).ready(function() {
	loadGraphList();
});


$("#createGraphButton").click(function(e) {
	var input = $("#createGraphInput").val();
	$("#createGraphInput").val(''); // clear value

	var thisButton = this;

	if (input === '' || input.indexOf(" ") !== -1 || input.indexOf("-") !== -1) {
		$("#message").html("<h3><small>Cannot be empty or contain spaces.</small></h3>");
	} else {

		$(thisButton).prop("disabled", true);
		$.ajax({
				type: "POST",
				url: "/check_graph/" + input,
				success: function(data) {
					if (data.exists === true) {
						$("#message").html("<h1><small>Already exists! Try another name.</small></h1>");
						$(thisButton).removeAttr("disabled");
					} else { // it exists
						$.ajax({
								type:"POST",
								url: "/create_graph/" + input,
								success: function(d) {
									loadGraphList();
									$(thisButton).removeAttr("disabled");
								}
						});
					}
				}
		});
	}
});