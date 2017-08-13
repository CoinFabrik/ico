const progress_bar = document.getElementById("progress_bar");
const submit_button = document.getElementById("submit_button");
const refresh_button = document.getElementById("refresh_button");
const phase_field = document.getElementById("phase_field");
const investor_count_field = document.getElementById("investor_count_field");

function send_request(method, body, on_ready_state) {
    const http_req = new XMLHttpRequest();
    http_req.open(method, "http://localhost:8080/");
    http_req.setRequestHeader("Content-Type", "application/json");
    http_req.onreadystatechange = function() {
        if (http_req.readyState == XMLHttpRequest.DONE && http_req.status == 200) {
            on_ready_state(http_req.response);
        }
    }
    http_req.send(JSON.stringify(body));
}


function refresh_state() {
    send_request("GET", { "method": "query_crowdsale" },  function(response) {
        const res = JSON.parse(response);
        let percent = (res.phase_progress / res.chunked_wei_multiple) * 100;
        progress_bar.style = "width: " + percent.toString() + "%";
        phase_field.textContent = "Current phase: " + res.current_phase.toString();
        // TODO: add investor count
        investor_count_field.textContent = res.investor_count.toString();
    });
}

refresh_button.addEventListener("click", () => refresh_state());
