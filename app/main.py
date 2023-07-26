from flask import Blueprint, jsonify
import requests
from tinkoff.invest import Client
from . import cache
import json
import tinkoff.invest as tinvest
import os


token = os.getenv('API_TOKEN')

main = Blueprint("main", __name__)
    

@main.route("/api/get-shares")
def index():
    shares = json.dumps(get_shares())
    return jsonify(shares)

@cache.cached(timeout=15)
def get_shares():
    
    with Client(token) as client:
        accounts = client.users.get_accounts().accounts
        data = []

        for account in accounts:
            if account.status != account.status.ACCOUNT_STATUS_CLOSED:
                portfolio = client.operations.get_portfolio(account_id=account.id)

                for position in portfolio.positions:
                    if position.instrument_type == "share":
                        share_name = client.instruments.share_by(
                                id_type=tinvest.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                                id=position.figi,
                            ).instrument.name
                        
                        share_info = {
                            'name': share_name,
                            'quantity': position.quantity.units,
                            'expected_yield': cast_money(position.expected_yield),
                            'average_buy_price': cast_money(position.average_position_price),
                            'currency': position.average_position_price.currency,
                            'nkd': cast_money(position.current_nkd)
                        }

                        share_info['sell_sum'] = (share_info['average_buy_price']*share_info['quantity'])+share_info['expected_yield']+(share_info['nkd']*share_info['quantity'])
                        share_info['comission'] = share_info['sell_sum']*0.003
                        share_info['tax'] = share_info['expected_yield']*0.013 if share_info['expected_yield'] > 0 else 0
                        
                        if share_info['currency'] != 'rub':
                            share_info = convert_to_rub(share_info)
                        
                        data.append(share_info)

        return data
    
@cache.cached(timeout=60)
def get_valutes():
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    if response.status_code == 200:
        return response.json()

def convert_to_rub(share):
    valutes = get_valutes()
    valute = valutes['Valute'][share['currency'].upper()]
    
    share['expected_yield'] = share['expected_yield']*valute['Value']
    share['average_buy_price'] = share['average_buy_price']*valute['Value']
    share['sell_sum'] = share['sell_sum']*valute['Value']
    share['comission'] = share['comission']*valute['Value']
    
    return share
    
    

def cast_money(value):
    return value.units + value.nano / 1e9
