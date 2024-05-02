import requests
import json
import time
import curses

open_order = None
completed_orders = 0

# Function to fetch BTCUSDT price from Binance API
def get_btcusdt_price():
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
        data = response.json()
        price = float(data['price'])
        return price
    except Exception as e:
        print('Error fetching BTCUSDT price from Binance:', e)
        return None

# Function to fetch order book data from Binance API
def fetch_order_book():
    try:
        response = requests.get('https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=100')
        data = response.json()
        bids = data['bids']
        asks = data['asks']

        # Calculate total bid quantity and ask quantity
        total_bid_quantity = sum(float(bid[1]) for bid in bids)
        total_ask_quantity = sum(float(ask[1]) for ask in asks)

        # Calculate percentage of buyers and sellers
        total_quantity = total_bid_quantity + total_ask_quantity
        buyers_percentage = (total_bid_quantity / total_quantity) * 100
        sellers_percentage = (total_ask_quantity / total_quantity) * 100

        return buyers_percentage, sellers_percentage
    except Exception as e:
        print('Error fetching order book data from Binance:', e)
        return None, None

# Function to create open order
def create_open_order(price):
    global open_order
    open_order = price
    print(f'Open order created at ${price}')

# Function to update price and percentages
def update_data(stdscr):
    global open_order
    global completed_orders

    while True:
        stdscr.clear()
        price = get_btcusdt_price()
        if price:
            stdscr.addstr(f'BTCUSDT Price: ${price}\n')
            buyers_percentage, sellers_percentage = fetch_order_book()
            if buyers_percentage is not None and sellers_percentage is not None:
                stdscr.addstr(f'Buyers Percentage: {buyers_percentage:.2f}%\n')
                stdscr.addstr(f'Sellers Percentage: {sellers_percentage:.2f}%\n')

                # Change font color based on buyer/seller dominance
                if buyers_percentage > sellers_percentage:
                    stdscr.addstr('\033[92m')  # Green color
                else:
                    stdscr.addstr('\033[91m')  # Red color
                stdscr.refresh()

                # Check if live price exceeds open order price by 0.01%
                if open_order is not None and price > open_order * 1.0001:
                    completed_orders += 1
                    stdscr.addstr(f'Order completed!\n')
                    open_order = None

                # Create open order if buying percentage is greater than 70%
                elif buyers_percentage > 70 and open_order is None:
                    create_open_order(price)
            else:
                stdscr.addstr('Failed to fetch order book data\n')
        else:
            stdscr.addstr('Failed to fetch BTCUSDT price\n')

        if open_order is not None:
            stdscr.addstr(f'Open Order Price: ${open_order}\n')

        stdscr.refresh()
        # print(f'BTCUSDT Price: ${price}')
        # print(f'Buyers Percentage: {buyers_percentage:.2f}%')
        # print(f'Sellers Percentage: {sellers_percentage:.2f}%')
        # print(f'Open Order Price: ${open_order}\n')
        print(f'Total completed orders: {completed_orders}\n')
        time.sleep(1)

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)  # Hide cursor
    curses.use_default_colors()
    update_data(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
