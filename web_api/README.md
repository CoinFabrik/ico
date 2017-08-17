The API server depends on web3, express and body-parser being installed globally through npm.
To launch the API server, execute `node rest_api.js`. By default, it listens on the port 8080.


The API server expects an HTTP GET request with a JSON body. The JSON must have a member named `method` of type string. There's only one supported method which is `query_crowdsale`. The server responds to such a request with another JSON in the body of the message. The response JSON contains the following members:

- `current_block`: The latest block number observed by the node.
- `starting_block`: The block in which the crowdsale starts.
- `ending_block`: The block in which the crowdsale ends.
- `wei_raised`: The amount of wei invested in the crowdsale.
- `investor_count`: The amount of investors that participated in the crowdsale.
- `crowdsale_finalized`: This is a flag that is only true once the crowdsale has been finalized which means that the tokens were released for transfer and the team received its 30% share of the total tokens.
- `funding_cap`: The funding cap of the crowdsale.
- `wei_per_phase`: Total wei per phase.
- `current_phase`: Current phase of the crowdsale.
- `phase_progress`: Amount of wei invested toward the current phase.

When an unsupported method is requested to the API server it responds with a JSON in the body with the member `error` set to a human-readable message string.

An example of how to use these values is in the web_test folder.