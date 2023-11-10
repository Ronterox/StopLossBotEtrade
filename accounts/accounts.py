from utilites.utilities import menu_select, is_float, cls, on_response_error


class Accounts:

    def __init__(self, session, base_url):
        self.session = session
        self.account = {}
        self.base_url = base_url
        pass

    @staticmethod
    def user_select_watch(symbol, pct_gain, left):
        percentage = ""
        quantity = ""
        proceed = ""

        while not is_float(percentage):
            percentage = input("Percentage change to auto-close (current %s%%): " % pct_gain)

        while not quantity.isdigit():
            quantity = input("Quantity to close (%s lefts): " % left)

        while proceed != 'y' and proceed != 'n':
            proceed = input(
                "You selected: \nOn %s%% lost, close %s positions of %s\nDo you want to continue? "
                "(y/n): " % (percentage, quantity, symbol))

        return float(percentage), quantity, proceed == 'y'

    def account_list(self):
        url = self.base_url + "/v1/accounts/list.json"
        response = self.session.get(url, header_auth=True)

        if response is not None and response.status_code == 200:
            data = response.json()
            try:
                accounts = data["AccountListResponse"]["Accounts"]["Account"]

                accounts[:] = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                length = len(accounts)

                if length == 1:
                    self.account = accounts[length - 1]
                else:
                    while True:
                        cls()

                        count = 0
                        print("\nBrokerage Account List:")

                        for account in accounts:
                            count = count + 1

                            print_str = str(count) + ")\t"

                            if account is not None:
                                def get_if_key(key, comma=True):
                                    return print_str + (',' if comma else '') + \
                                           account[key].strip() if account[key] else print_str

                                print_str = get_if_key("accountId", False)
                                print_str = get_if_key("accountDesc")
                                print_str = get_if_key("institutionType")

                            print(print_str)

                        print(str(count) + ")\t" "Exit")

                        # Select account option
                        account_index = input("Please select an account: ")

                        if account_index.isdigit() and 0 < int(account_index) < count:
                            self.account = accounts[int(account_index) - 1]
                            break
                        elif account_index == str(count):
                            break
                        else:
                            print("Unknown Account Selected!")

            except KeyError:
                on_response_error(response, "AccountList")
        else:
            on_response_error(response, "AccountList")

    pass

    def request_position(self, _id):
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/portfolio.json"
        response = self.session.get(url, header_auth=True)

        if response is not None and response.status_code == 200:
            data = response.json()

            if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:
                for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                    if acctPortfolio is not None and "Position" in acctPortfolio:
                        for position in acctPortfolio["Position"]:
                            if position["positionId"] == _id:
                                return response, position
        return response, None

    def watch_position(self, key, _id, percentage, quantity, highest_pct):
        from time import sleep

        checking = True

        response, position = None, None

        while checking:
            sleep(1)

            response, position = self.request_position(_id)

            if position is not None:
                current_gain = float(position["totalGainPct"])

                if current_gain > highest_pct:
                    highest_pct = current_gain
                else:
                    pct_lost = 100 - current_gain / highest_pct * 100 if highest_pct != 0 else current_gain
                    print("Percentage Lost is: ", '{:,.2f}%'.format(pct_lost))

                    checking = abs(pct_lost) < percentage

                print("Highest Pct is: ", highest_pct, "\nCurrent ", current_gain, "\n")
            else:
                on_response_error(response, "Portfolio")

        closed = self.close_order(key, quantity, position)
        counter = 3
        while not closed and counter > 0:
            sleep(1)
            closed = self.close_order(key, quantity, position)
            counter = counter - 1

    pass

    def close_order(self, key, quantity, position):
        from order.orders import Orders

        orders = Orders(self.session, self.account, self.base_url)

        order = Orders.create_close_order(quantity, position["Product"])
        headers, preview_payload = Orders.create_order_request_params(key, order)

        preview_id = orders.preview_order(headers, preview_payload)

        if preview_id:
            headers, payload = Orders.create_order_request_params(key, order, "PlaceOrderRequest", preview_id)
            return orders.place_order(headers, payload)
        return False

    def portfolio(self, key):
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/portfolio.json"

        response = self.session.get(url, header_auth=True)

        print("\nPortfolio:")

        if response is not None and response.status_code == 200:
            data = response.json()

            if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:

                for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                    if acctPortfolio is not None and "Position" in acctPortfolio:
                        count = 0
                        positions = []
                        for position in acctPortfolio["Position"]:
                            def format_money(money):
                                return str('${:,.2f}'.format(money))

                            symbol = position["symbolDescription"]
                            pct_gain = position["totalGainPct"]
                            quantity = position["quantity"]

                            positions.append((position["positionId"], symbol, pct_gain, quantity))

                            try:
                                print_str = "Symbol: " + str(symbol)
                                print_str = print_str + " | Quantity #: " + str(quantity)
                                print_str = print_str + " | Percentage Gain: " + str('{:,.2f}%'.format(pct_gain))
                                print_str = print_str + " | Total Gain: " + format_money(position["totalGain"])

                                count = count + 1
                                print(str(count) + ") " + print_str)

                            except KeyError:
                                print("Key Error")

                        print(str(count + 1) + ") Exit")

                        selection = ""
                        while not selection.isdigit() or not int(selection) > 0 or not int(selection) <= len(
                                positions) + 1:
                            selection = input("Please select a position: ")

                        if int(selection) < len(positions) + 1:
                            id_select, symbol, pct_gain, left = positions[int(selection) - 1]

                            response, position = self.request_position(id_select)

                            if response is not None:
                                if "callPut" in position["Product"]:
                                    percentage, quantity, proceed = Accounts.user_select_watch(symbol, pct_gain, left)

                                    if proceed:
                                        self.watch_position(key, id_select, percentage, quantity, pct_gain)
                                else:
                                    print("The position is not a Trading Option!")
                            else:
                                on_response_error(response, "Account")
                    else:
                        print("None")
            else:
                on_response_error(response, "Portfolio")
        elif response is not None and response.status_code == 204:
            print("None")
        else:
            on_response_error(response, "Portfolio")

    pass

    def account_menu(self, key):
        cls()

        if self.account["institutionType"] == "BROKERAGE":
            self.portfolio(key)
        else:
            while True:
                selection = menu_select({"1": "Exit"})
                if selection == "1":
                    break
                else:
                    print("Unknown Option Selected!")


pass
