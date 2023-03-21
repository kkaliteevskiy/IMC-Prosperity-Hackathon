# create an example trading state which can be used to test trading algorithm

from datamodel import Listing, OrderDepth, Trade, TradingState

timestamp = 1000

listings = {
	"PEARLS": Listing(
		symbol="PEARLS", 
		product="PEARLS", 
		denomination= "SEASHELLS"
	),
	"BANANAS": Listing(
		symbol="BANANAS", 
		product="BANANAS", 
		denomination= "SEASHELLS"
	),
}

order_depths = {
	"PEARLS": OrderDepth(
		buy_orders={9100: 7, 9000: 5},
		sell_orders={9900: -4, 9970: -8, 11000: -5}
	),
	"BANANAS": OrderDepth(
		buy_orders={4801: 3, 4700: 5},
		sell_orders={4940: -5, 4950: -8}
	),	
}

own_trades = {
	"PEARLS": [],
	"BANANAS": []
}

market_trades = {
	"PEARLS": [
		Trade(
			symbol="PEARLS",
			price=10000,
			quantity=4,
			buyer="",
			seller="",
			timestamp=900
		)
	],
	"BANANAS": []
}

position = {
	"PEARLS": 3,
	"BANANAS": -5
}

observations = {}

state = TradingState(
	timestamp=timestamp,
  listings=listings,
	order_depths=order_depths,
	own_trades=own_trades,
	market_trades=market_trades,
    position=position,
    observations=observations
)