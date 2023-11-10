import configparser
from accounts.accounts import Accounts
from order.orders import Orders
from utilites.utilities import login


def test_order():
    config = configparser.ConfigParser()
    config.read('../config.ini')

    session, base_url = login(config)

    if session is not None:
        account = Accounts(session, base_url)
        account.account_list()

        if account.account:
            order = Orders(session, account.account, base_url)
            # order.preview_order(config["DEFAULT"]["CONSUMER_KEY"], Order.create_close_order("GOOG", 2, "CALL"))
    pass


if __name__ == '__main__':
    test_order()
