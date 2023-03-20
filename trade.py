# Code which will be required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # set position limits and estimate fair values
        positionLimits = {'PEARLS': 20, 'BANANAS': 20}
        productValuations = {'PEARLS': 10000, 'BANANAS': 4800}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # Define a fair value
            acceptable_price = productValuations[product]

            # get current position on the product
            currentPosition = state.position[product]

            # If statement checks if there are any SELL orders in the market
            if len(order_depth.sell_orders) > 0:

                # Sort all the available sell orders by their price,
                # and select only the sell order with the lowest price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = -1*order_depth.sell_orders[best_ask]

                # Check if the lowest ask (sell order) is lower than the above defined fair value
                if best_ask < acceptable_price:

                    # decide how much to buy
                    quantityToBuy = decideHowMuchToBuy(currentPosition, best_ask_volume, positionLimits[product])
                    # update current position
                    currentPosition += quantityToBuy
                    
                    # We expect this order to trade with the sell order
                    print(product, "BUY", str(quantityToBuy) + "x", best_ask)
                    orders.append(Order(product, best_ask, quantityToBuy))

            # The below code block is similar to the one above,
            # the difference is that it finds the highest bid (buy order)
            # If the price of the order is higher than the fair value
            # This is an opportunity to sell at a premium
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price:
                    if currentPosition - best_bid_volume > -positionLimits[product]:
                        # safe to sell all available at this price
                        quantityToSell = best_bid_volume
                    else:
                        quantityToSell = positionLimits[product] + currentPosition

                    print(product, "SELL", str(quantityToSell) + "x", best_bid)
                    orders.append(Order(product, best_bid, -quantityToSell))

            # Add all the above orders to the result dict
            result[product] = orders

            # Return the dict of orders
            # These possibly contain buy or sell orders depending on the logic above
        # print for debugging purposes 
        print("Printing output: ")
        print(result)

        return result

def decideHowMuchToBuy(currentPos, maxPossibleVolume, positionLimit):
    """ Decide how much of a product to buy, given that there is at least some available at a fair price
    Takes as input the current position on the product in question, the position limit for that product and the
    max available to buy at the one specific price point
    Returns how much can be bought at that price"""
    if currentPos + maxPossibleVolume <= positionLimit:
        # can buy all available at that price without reaching position limit
        quantityToBuy = maxPossibleVolume
    else:
        # buy just enough to reach the position limit
        # *** might not be a great strategy to do this every time...
        quantityToBuy = positionLimit - currentPos
    # update current position
    return quantityToBuy