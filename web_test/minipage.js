const submit_button = document.getElementById("submit_button");
const refresh_button = document.getElementById("refresh_button");
const starting_timestamp_field = document.getElementById("starting_timestamp_field");
const ending_timestamp_field = document.getElementById("ending_timestamp_field");
const investor_count_field = document.getElementById("investor_count_field");
const minimum_buy_field = document.getElementById("minimum_buy_field");
const sold_tokens_field = document.getElementById("sold_tokens_field");

function send_request(method, on_ready_state) {
    const http_req = new XMLHttpRequest();
    http_req.open(method, "./?method=query_crowdsale");
    http_req.setRequestHeader("Content-Type", "application/json");
    http_req.onreadystatechange = function() {
        if (http_req.readyState == XMLHttpRequest.DONE && http_req.status == 200) {
            on_ready_state(http_req.response);
        }
    }
    http_req.send();
}


function refresh_state() {
    send_request("GET",  function(response) {
        // For debugging purposes
        console.log("Unparsed JSON:");
        console.log(response);
        if (response.error) {
            console.log('The server responded with an error: "' + response.error + '"');
            return;
        }
        const res = JSON.parse(response);
        // For debugging purposes
        console.log("Parsed JSON:");
        console.log(res);
        starting_timestamp_field.textContent = res.starting_timestamp.toString();
        ending_timestamp_field.textContent = res.ending_timestamp.toString();
        investor_count_field.textContent = res.investor_count.toString();
        minimum_buy_field.textContent = res.minimum_buy.toString();
        sold_tokens_field.textContent = res.sold_tokens.toString();
    });
}

refresh_button.addEventListener("click", () => refresh_state());
