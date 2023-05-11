$.ajax({
    url: "/get_data",
    type: "GET",
    success: function(response){
        try {
            let data = JSON.parse(response);
            let table = $('#myTable').DataTable();
            table.clear();
            table.rows.add(data);
            table.draw();
        } catch(e) {
            console.error("An error occurred while processing the response: ", e);
        }
    },
    error: function(xhr){
        console.error("An error occurred while making the request: ", xhr.statusText);
    }
});
