import configparser
import json
from utilites.utilities import login
from accounts.accounts import Accounts


def test_login():
    config = configparser.ConfigParser()
    config.read('../config.ini')

    session, base_url = login(config)

    if session is not None:
        account = Accounts(session, base_url)
        account.account_list()

        url = base_url + "/v1/accounts/" + account.account["accountIdKey"] + "/portfolio.json"

        response = session.get(url, header_auth=True)

        parsed = json.loads(response.text)

        print(json.dumps(parsed, indent=4))

        # url = base_url + "/v1/accounts/" + account.account["accountIdKey"] + "/portfolio/27005131.json"
        # response = session.get(url, header_auth=True)
        #
        # print(response.text)

    pass


if __name__ == '__main__':
    test_login()
