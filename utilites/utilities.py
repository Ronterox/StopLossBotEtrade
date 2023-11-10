def menu_select(menu_items):
    print("")
    for position in menu_items.keys():
        print(position + ")\t" + menu_items[position])

    return input("Please select an option: ")


def on_response_error(response, api_name):
    error_text = "Error: "

    try:
        if response is not None and response.headers['Content-Type'] == 'application/json':
            error_text = "Error: " + response.json()["Error"]["message"]
    except KeyError:
        error_text = "Error: %s API service error" % api_name

    print(error_text)
    pass


def is_float(a_string):
    try:
        float(a_string)
        return True
    except ValueError:
        return False
    pass


def cls():
    print("\033[H\033[2J", end="")


def oauth(base_url, config):
    from rauth import OAuth1Service
    import webbrowser

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config["CONSUMER_KEY"],
        consumer_secret=config["CONSUMER_SECRET"],
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url=base_url)

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(params={"oauth_callback": "oob", "format": "json"})

    # Step 2: Go through the authentication flow. Login to E*TRADE.
    # After you login, the page will provide a text code to enter.
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")

    # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    session = etrade.get_auth_session(request_token,
                                      request_token_secret,
                                      params={"oauth_verifier": text_code})
    return session
