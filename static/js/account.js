$("#createGraphButton").click(function(e) {
	var input = $("#createGraphInput").val();
	console.log(input);
	if (input === '' || input.indexOf(" ") !== -1) {
		alert('Cannot be empty or contain spaces');
	} else {

		$.ajax({
				type: "POST",
				url: "/check_graph/" + input,
				success: function(data) {
					if (data.exists === true) {
						alert("graph name already exists, try again!");
					} else { // it exists
						$.ajax({
								type:"POST",
								url: "/create_graph/" + input,
								success: function(d) {
									window.location.href = 'http://localhost:8000/graph/' + input;
								}
						});
					}
				}
		});
	}
});