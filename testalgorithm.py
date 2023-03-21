# file to test the current trading algorithm using the example trading state

from createtradingstate import state
from trade import Trader

    
trader = Trader()
trader.run(state)