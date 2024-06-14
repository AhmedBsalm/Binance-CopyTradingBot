import os
import json
import logging
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import asyncio
from httpx import AsyncClient,ConnectTimeout,NetworkError

load_dotenv()

log_filename = os.path.join(os.path.dirname(__file__), 'trade.log')
trade_info_file = os.path.join(os.path.dirname(__file__), 'trader.json') 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.getLogger('').addHandler(file_handler)



class Copytrader():
    headers = {
        'x-rapidapi-key': os.getenv('KEY'),
        'x-rapidapi-host': "binance-futures-leaderboard1.p.rapidapi.com"
    }
    def __init__(self, apiKey, secretKey, leverage,usdtAmount, traderUUID):
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.leverage = leverage
        self.usdtAmount = usdtAmount
        self.UUID = traderUUID

    async def trade(self, symbol, direction, decimals):
        # with open(trade_info_file) as f:
        #     trade_info = json.load(f)
        trade = {'bybit_api_key': self.apiKey, 'bybit_api_secret': self.secretKey, 'leverage': self.leverage, 'usdt_amount': self.usdtAmount,"leveragetype": 1}
        logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        if trade == []:
            logging.info("No data to trade")
        else:
                print('Trading Started')
            # Loop through each trade in trade_info
            # for trade in trade_info:
                try:
                    session = HTTP(api_key=trade['bybit_api_key'], api_secret=trade['bybit_api_secret'])
                except Exception as e:
                    logging.error(f"Error creating authenticated session for {symbol} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Error: {e}")
                try:
                    response = session.switch_margin_mode(
                        category="linear",
                        symbol=symbol,
                        tradeMode=int(trade['leveragetype']),
                        buyLeverage=trade['leverage'],
                        sellLeverage=trade['leverage'],
                            )

                    if response['retMsg'] == 'OK':
                        logging.info(f"margin mode set successfully for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}")
                    else:
                        logging.error(f"Error setting margin mode for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Response: {response}")
                except Exception as e:
                    logging.error(f"Error setting margin mode for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Error: {e}")
                    logging.info("Continuing to place order...")

                try:
                    response = session.set_leverage(
                        category="linear",
                        symbol=symbol,
                        buyLeverage=trade['leverage'],
                        sellLeverage=trade['leverage'],
                    )

                    if response['retMsg'] == 'OK':
                        logging.info(f"Leverage set successfully for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}")
                    else:
                        logging.error(f"Error setting leverage for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Response: {response}")
                except Exception as e:
                    logging.error(f"Error setting leverage for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Error: {e}")
                    logging.info("Continuing to place order...")

                try:
                    response = session.get_tickers(
                        category="linear",
                        symbol=symbol,
                    )

                    if response and 'result' in response and 'list' in response['result'] and len(response['result']['list']) > 0:
                        price = float(response['result']['list'][0].get('lastPrice', None))
                        if price is not None:
                            usdt_size = float(trade['usdt_amount']) 
                            size = usdt_size * int(trade['leverage'])
                            size = round(usdt_size / price, decimals)
                            size = round(size * int(trade['leverage']), decimals)
                            logging.info(f"Placing a market order to buy {size} contracts of {symbol} at {price} USDT per contract for {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}.")

                            try:
                                response = session.place_order(
                                    category="linear",
                                    symbol=symbol,
                                    side=direction,
                                    orderType="Market",
                                    qty=float(size),
                                    leverage=int(trade['leverage']),
                                )

                                if 'result' in response and response['result']:
                                    logging.info(f"Trade placed successfully for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Response: {response}")
                                else:
                                    logging.error(f"Error placing trade for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Response: {response}")

                            except Exception as e:
                                logging.error(f"Error placing trade for {symbol} {direction} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Leverage: {trade['leverage']}. Error: {e}")
                                logging.info("Continuing to next trade...")

                        else:
                            logging.error(f"Error getting ticker data for {symbol}. Last price not found. Response: {response}")

                    else:
                        logging.error(f"Error getting ticker data for {symbol}. Response: {response}")

                except Exception as e:
                    logging.error(f"Error getting ticker data for {symbol}. Error: {e}")
                    logging.info("Continuing to next trade...")



    async def close_trade_on_symbol(self, symbol):
        # with open(trade_info_file) as f:
        #     trade_info = json.load(f)
        trade = {'bybit_api_key': self.apiKey, 'bybit_api_secret': self.secretKey, 'leverage': self.leverage, 'usdt_amount': self.usdtAmount,"leveragetype": 1,
            "size": 5}
        logging.basicConfig(filename='trade.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        if trade == []:
            logging.info("No data to close trade")
        else :
                try:
                    session = HTTP(api_key=trade['bybit_api_key'], api_secret=trade['bybit_api_secret'])

                    response = session.get_positions(
                        category="linear",
                        symbol=symbol,
                    )

                    if response and 'result' in response and 'list' in response['result'] and len(response['result']['list']) > 0:
                        for position in response['result']['list']:
                            size = float(position['size'])
                            side = position['side']

                            opposite_direction = "Sell" if side == "Buy" else "Buy"
                            mode = 1 if side == "Buy" else 2
                            response = session.place_order(
                                category="linear",
                                symbol=symbol,
                                side=opposite_direction,
                                orderType="Market",
                                qty=float(size),
                                positionIdx=mode
                            )

                            if 'result' in response and response['result']:
                                logging.info(f"Trade closed successfully for {symbol} {side} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Response: {response}")
                            else:
                                logging.error(f"Error closing trade for {symbol} {side} trade. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Response: {response}")

                    else:
                        logging.error(f"Error getting position data for {symbol}. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Response: {response}")

                except Exception as e:
                    logging.error(f"An error occurred while processing trade for {symbol}. API keys: {trade['bybit_api_key']}, {trade['bybit_api_secret']}. Error: {e}")
    def calculateDecimals(self, amount):
        stringAM = str(amount)
        if '.' in stringAM:
            bef, decimals = stringAM.split('.')
            return len(decimals)
        else:
            return 0

    async def run(self, user):
        params = {
        'encryptedUid': self.UUID,
        'tradeType': 'PERPETUAL',
    }
        counter = 0 
        no_change_threshold = 30
        filename = os.path.join(os.path.dirname(__file__), f'symbols{str(user).upper()}.json')
        previous_symbols = {}

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    previous_symbols = json.load(f)
                except json.JSONDecodeError:
                    pass
        while True:
            try:
                async with AsyncClient() as http_client:
                    response = await http_client.get("https://binance-futures-leaderboard1.p.rapidapi.com/v2/getTraderPositions?tradeType=ALL", headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    print(data)



                    current_symbols = {}
                    if data['data'][0]['positions']['perpetual']:
                        for item in data['data'][0]['positions']['perpetual']:
                            
                            amount = item['amount']
                            symbol = item['symbol']
                            current_symbols[symbol] = amount

                        new_symbols = set(current_symbols.keys()) - set(previous_symbols.keys())
                        removed_symbols = set(previous_symbols.keys()) - set(current_symbols.keys())

                        symbols_added = []
                        symbols_removed = []
                        symbols_with_increased_amount = []

                        if new_symbols:
                            symbols_added = list(new_symbols)
                            logging.info(f"New symbols found: {symbols_added}")
                            for symbol in symbols_added:
                                if current_symbols[symbol] > 0:
                                    await self.trade(symbol, "Buy", self.calculateDecimals(current_symbols[symbol]))
                                elif current_symbols[symbol] < 0:
                                    await self.trade(symbol, "Sell",self.calculateDecimals(current_symbols[symbol]))
                        if removed_symbols:
                            symbols_removed = list(removed_symbols)
                            logging.info(f"Removed symbols: {symbols_removed}")
                            for symbol in removed_symbols:
                                await self.close_trade_on_symbol(symbol)
                            

                        for symbol in current_symbols:
                            if symbol in previous_symbols and abs(current_symbols[symbol]) > abs(previous_symbols[symbol]):
                                increase_percentage = abs(current_symbols[symbol] - previous_symbols[symbol]) / abs(previous_symbols[symbol])
                                if increase_percentage >= 1.5:
                                    symbols_with_increased_amount.append(symbol)
                                    logging.info(f"Symbol {symbol} amount increased: {previous_symbols[symbol]} -> {current_symbols[symbol]}")
                                    if current_symbols[symbol] > previous_symbols[symbol]:
                                        direction = "Buy"
                                    else:
                                        direction = "Sell"
                                    await self.trade(symbol, direction)


                        if not symbols_added and not symbols_removed and not symbols_with_increased_amount:
                            counter += 1 # increment counter
                            if counter == no_change_threshold:
                                logging.info("No changes")
                                counter = 0 # reset counter

                        previous_symbols = current_symbols

                        with open(filename, 'w') as f:
                            json.dump(previous_symbols, f)

            except (ConnectTimeout, NetworkError) as e:
                            print(f"Network error: {e}. Retrying in {5} seconds...")
                            await asyncio.sleep(5) 
            await asyncio.sleep(1) 

# asyncio.run(main())