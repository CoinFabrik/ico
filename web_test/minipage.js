const progress_bar = document.getElementById("progress_bar");
const submit_button = document.getElementById("submit_button");
const refresh_button = document.getElementById("refresh_button");
const phase_field = document.getElementById("phase_field");
const block_number_field = document.getElementById("block_number_field");
const starting_block_field = document.getElementById("starting_block_field");
const ending_block_field = document.getElementById("ending_block_field");
const start_eta_field = document.getElementById("start_eta_field");
const end_eta_field = document.getElementById("end_eta_field");
const funding_cap_field = document.getElementById("funding_cap_field");
const minimum_goal_field = document.getElementById("minimum_goal_field");
const investor_count_field = document.getElementById("investor_count_field");

function send_request(method, on_ready_state) {
    const http_req = new XMLHttpRequest();
    http_req.open(method, "http://localhost:8080/?method=query_crowdsale");
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
        let percent = (res.phase_progress / res.ether_per_phase) * 100;
        progress_bar.style = "width: " + percent.toString() + "%";
        phase_field.textContent = "Current phase: " + res.current_phase.toString();
        block_number_field.textContent = res.current_block.toString();
        starting_block_field.textContent = res.starting_block.toString();
        ending_block_field.textContent = res.ending_block.toString();
        start_eta_field.textContent = res.start_eta.toString();
        end_eta_field.textContent = res.end_eta.toString();
        funding_cap_field.textContent = res.cap.toString();
        minimum_goal_field.textContent = res.minimum_goal.toString();
        investor_count_field.textContent = res.investor_count.toString();
    });
}

refresh_button.addEventListener("click", () => refresh_state());
