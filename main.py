import configparser
from accounts.accounts import Accounts
from utilites.utilities import oauth


def main():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding="utf-8")

    config = config["DEFAULT"]
    base_url = config["PROD_BASE_URL"]

    session = oauth(base_url, config)

    if session is not None:
        account = Accounts(session, base_url)
        account.account_list()

        if account.account:
            account.account_menu(config["CONSUMER_KEY"])
    pass


if __name__ == '__main__':
    main()
