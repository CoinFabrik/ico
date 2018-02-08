The API server depends on web3 and express being installed globally through npm.
To launch the API server, execute `node rest_api.js`. By default, it listens on the port 8080.


The API server expects an HTTP GET request with a query string encoded `method` field. There's only one supported method which is `query_crowdsale`. The server responds to such a request with a JSON in the body of the message. In short, the query string should be: "?method=query_crowdsale". The JSON in the response describes an object that contains the following members:

- `current_block`: The latest block number observed by the node.
- `starting_timestamp`: The UTC timestamp in which the crowdsale starts.
- `ending_timestamp`: The UTC timestamp in which the crowdsale ends.
- `sold_tokens`: The amount of tokens that have been sold in the crowdsale.
- `investor_count`: The amount of investors that participated in the crowdsale.
- `finalized`: A flag that is only true once the crowdsale has been finalized which means that the tokens were released for transfer and the team received the remaining tokens.
- `minimum_buy`: The minimum amount of ethers that is accepted as a contribution.


Currency parameters are sent as a string since that's the most precise serialization for a BigNumber. Using wei values in plain javascript calculations may lose some precision unless the string is deserialized into a BigNumber first. For statistical purposes an exact calculation may not be necessary though.

When an unsupported method is requested to the API server instead, it responds with a JSON in the body with the member `error` set to a human-readable message string.

An example of how to use these values is in the web_test folder.
