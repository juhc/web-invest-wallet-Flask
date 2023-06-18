from flask import Blueprint, render_template
from tinkoff.invest import (
    Client,
    GenerateBrokerReportRequest,
    GetBrokerReportRequest,
    InstrumentStatus,
)
import tinkoff.invest as tinvest
from datetime import datetime, timedelta
import pandas as pd


main = Blueprint("main", __name__)


@main.route("/")
def index():
    get_shares()
    return "AAAA"


def get_shares():
    token = ""

    with Client(token) as client:
        accounts = client.users.get_accounts().accounts
        data = []

        for account in accounts:
            if account.status != account.status.ACCOUNT_STATUS_CLOSED:
                print(account.name)
                portfolio = client.operations.get_portfolio(account_id=account.id)

                for position in portfolio.positions:
                    if position.instrument_type == "share":
                        share_name = client.instruments.share_by(
                                id_type=tinvest.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                                id=position.figi,
                            ).instrument.name
                        
                        d = {
                            'name': share_name,
                            'quantity': position.quantity.units,
                            'expected_yield': cast_money(position.expected_yield),
                            'average_buy_price': cast_money(position.average_position_price),
                            'currency': position.average_position_price.currency,
                            'nkd': cast_money(position.current_nkd)
                        }

                        d['sell_sum'] = (d['average_buy_price']*d['quantity'])+d['expected_yield']+(d['nkd']*d['quantity'])
                        d['comission'] = d['sell_sum']*0.003
                        d['tax'] = d['expected_yield']*0.013 if d['expected_yield'] > 0 else 0
                        data.append(d)

        df = pd.DataFrame(data)
        

        print(df)

def cast_money(value):
    return value.units + value.nano / 1e9
