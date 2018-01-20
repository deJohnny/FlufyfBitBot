from bifenixClient import *
from random import uniform
import time
import requests
import numpy as np
import pickle


class State(object):
    SLEEPING = 0
    GENERIC = 1
    BOUGHT_FIRST = 2
    SOLD_FIRST = 3
    GENERIC_TRYING_TO_BUY = 4
    GENERIC_TRYING_TO_SELL = 5
    TRYING_TO_SELL = 6
    TRYING_TO_BUY = 7


# this is secret, should hide it
api_key = 'brxC0OSSAk7JjFMFt5rJZF7FKmqd6pnhRGhf6LaZkB8'
secret = 'huLeDy6aN9FVNqUjyLiyhMfRB3b2luonbzdqbZszMwA'

g_dealingAmount = 0.005
g_secs_to_defualt_sellOrBuy = 60*30

g_profit_till_now = 0
g_profit_counter_till_now = 0

def closeUnfinishedDeals():
    global myClient
    ans = orderbook(symbol='btcusd')
    ask = float(ans['asks'][0]['price'])
    bid = float(ans['bids'][0]['price'])
    maxNodes = 400
    graph_data = open('allDeals.csv', 'r').read()
    lines = graph_data.split('\n')
    lastAct = -1

    for node in xrange(0,maxNodes):
        parity = 0
        for line in lines:
            if len(line) > 1:
                sORb, nodeId, thisTime, thisPrice, thisProfit  = line.split(',')
                if float(nodeId) == node:
                    parity += 1
                    lastAct = int(sORb)
                    lastPrice = float(thisPrice)

        if (parity % 2) == 1:
            if lastAct == 0:
                sellPrice = 1.01 * lastPrice / (0.998 * 0.998)
                if sellPrice > bid:
                    trade = place_order(amount=g_dealingAmount, price=int(round(sellPrice)), side='sell',
                                        ord_type='exchange limit',
                                        symbol='btcusd',
                                        exchange='all')
                else:
                    trade = place_order(amount=g_dealingAmount, price=int(round(bid)), side='sell',
                                        ord_type='exchange limit',
                                        symbol='btcusd',
                                        exchange='all')
            else:
                buyPrice = (0.998 * 0.998)*lastPrice/1.01
                if buyPrice < bid:
                    trade = place_order(amount=g_dealingAmount, price=int(round(buyPrice)), side='sell',
                                        ord_type='exchange limit',
                                        symbol='btcusd',
                                        exchange='all')
                else:
                    trade = place_order(amount=g_dealingAmount, price=int(round(bid)), side='sell',
                                        ord_type='exchange limit',
                                        symbol='btcusd',
                                        exchange='all')

    open("allDeals.csv", 'w').close()


closeUnfinishedDeals()




# those are global vars
g_daysTillValueLoop = 2

g_dealingAmountInDollar = g_dealingAmount * 16000
g_activeAgents = 0


g_totalDollarAmount = float(balances()[1]['available'])
lastPrice = float(trades()[0]['price'])

g_numberOfAgents = int(round(g_totalDollarAmount / lastPrice / g_dealingAmount))


g_myActiveBitcoins = float(balances()[0]['available'])
g_numberOfAgents = g_numberOfAgents + int(round(g_myActiveBitcoins / g_dealingAmount))

g_last_history_scan=0

print g_myActiveBitcoins
print g_totalDollarAmount

def update_number_of_agents(ask):
    global g_myActiveBitcoins
    global g_totalDollarAmount
    global g_last_history_scan
    while True:
        try:
            ans = balances()
            g_myActiveBitcoins = float(ans[0]['available'])
            g_totalDollarAmount = float(ans[1]['available'])
        except Exception as ex:
            print ans
            time.sleep(61)
            continue
        break
    g_last_history_scan=time.time()



# if g_last_history_scan + 60 * 60 * 0.5 < thisTime
#     update_number_of_agents(ask)

# todo: def closeUnfinishedDeals():

# todo: get to top and down from history and historesis
g_over_this_you_should_not_buy = 14335.0
g_under_this_you_should_not_sell = 13517.0

g_all_deals_history = pickle.load(open('all_echange_history.p'))

def get_starting_history(days_back):
    global g_all_deals_history
    startingTime = int(int(round(time.time())) - 60 * 60 * 24 * days_back)
    stopingTime = int(int(round(time.time())) - 60 * 2)
    lastTime = startingTime
    lastlastTime = 0
    bFirsrRun = 1

    while int(lastTime) < int(stopingTime):
        time.sleep(3)
        try:
            r = requests.get(
                'https://api.bitfinex.com/v2/trades/tBTCUSD/hist?start=' + str(lastTime) + '000&sort=1&limit=1000 ',
                verify=False)
            ans = r.json()
            lastTime = int(ans[-1][1])
        except Exception as ex:
            print ans
            time.sleep(61)
            continue

        if lastlastTime == lastTime:
            break
        else:
            lastlastTime = lastTime

        ans = r.json()
        if bFirsrRun == 1:
            bFirsrRun = 0
            g_all_deals_history = ans
        else:
            g_all_deals_history = g_all_deals_history + ans
        lastTime = int(ans[-1][1])
        lastTime = int(round(lastTime / 1000))
        print lastTime

    pickle.dump(g_all_deals_history, open('all_echange_history.p', 'w'))
    return

# get_starting_history(2)
print 'hi'


def update_all_deals_history():
    global g_all_deals_history
    lastTime = int(round(float((g_all_deals_history[-1][1])) /1000 ))
    stopingTime = int(int(round(time.time()) - 60 * 2))

    lastlastTime = int(g_all_deals_history[-1][1])

    while int(lastTime) < int(stopingTime):
        time.sleep(3)
        try:
            r = requests.get(
                'https://api.bitfinex.com/v2/trades/tBTCUSD/hist?start=' + str(lastTime) + '000&sort=1&limit=1000 ',
                verify=False)
            ans = r.json()
            lastTime = int(ans[-1][1])
        except Exception as ex:
            print ans
            time.sleep(61)
            continue

        if lastlastTime == lastTime:
            break
        else:
            lastlastTime = lastTime

        ans = r.json()

        g_all_deals_history = g_all_deals_history + ans
        lastTime = int(ans[-1][1])
        lastTime = int(round(lastTime)/1000)

    pickle.dump(g_all_deals_history, open('all_echange_history.p', 'w'))
    return

g_last_history_scan = 0

def get_up_down_percentile():
    global g_over_this_you_should_not_buy
    global g_under_this_you_should_not_sell
    global g_last_history_scan

    startingTime = int(int(round(time.time()) - 60 * 60 * 2)*1000)

    allPrices = []
    # get_starting_history(0.3)
    update_all_deals_history()
    # lines = get_long_history(2)
    # lines = rawList.split('\n')
    for indx in xrange(len(g_all_deals_history)-2):

        if startingTime > float(g_all_deals_history[indx][1]):
            continue

        allPrices.append(float(g_all_deals_history[indx][3]))

    allPrices = np.array(allPrices)
    g_over_this_you_should_not_buy = np.percentile(allPrices, 55)
    g_under_this_you_should_not_sell = np.percentile(allPrices, 45)

    return

# get_up_down_percentile()

# global funcs :

def g_get_time():
    return time.time()

def g_get_next_activate_time():
    return g_get_time() + uniform(0, 60 * 60 * 4 )

# global funcs :
def g_get_first_activate_time():
    return g_get_time() + uniform(0, 60 * 60 * 4)




def g_sell_bitcoin(price):

    while True:
        trade = place_order(amount=g_dealingAmount, price=1, side='sell', ord_type='exchange market', symbol='btcusd', exchange='all')

        try:
            ans = float(trade['price'])
        except Exception as ex:
            print("Caught exception {}".format(ex))
            print trade
            time.sleep(20)
            continue
        break
    return ans


def g_buy_bitcoin(price):

    while True:
        trade = place_order(amount=g_dealingAmount, price=99999, side='buy', ord_type='exchange market', symbol='btcusd', exchange='all')

        try:
            ans = float(trade['price'])
        except Exception as ex:
            print("Caught exception {}".format(ex))
            print trade
            time.sleep(20)
            continue
        break

    return ans

def g_activated_agent(his_id):
    global g_activeAgents
    g_activeAgents = g_activeAgents + 1

def g_deactivated_agent(his_id):
    global g_activeAgents
    g_activeAgents = g_activeAgents - 1

# end of global funcs


class ActualTrader:
    def __init__(self, this_id, win_percentage):
        # setting all private vars
        print win_percentage
        self._winPercentage = win_percentage
        self._id = this_id
        if self._id <= (g_numberOfAgents/2):
            self._myState = State.SLEEPING
            self._activateTime = g_get_first_activate_time()
            print self._id
        if self._id > (g_numberOfAgents/2):
            self._myState = State.SLEEPING
            self._activateTime = g_get_next_activate_time()
            print self._id
            print self._id
        if self._id == 0:
            self._myState = State.GENERIC
            g_activated_agent(self._id)
        self._histSellLim = -1
        self._sellPoint = -1
        self._minSellPrice = -1
        self._maxBuyPrice = -1
        self._buyPoint = -1
        self._histBuyLim = -1
        self._globalMin = 9999999
        self._globalMax = -1
        self._finBoughtPrice = -1
        self._finSoldPrice = -1

        self._gotPastHisteresisTime = -1




    def _go_to_sleep(self):
        if self._id == 0:
            self._myState = State.GENERIC
        else:
            self._myState = State.SLEEPING
            g_deactivated_agent(self._id)
            self._activateTime = g_get_next_activate_time()
        self._histSellLim = -1
        self._sellPoint = -1
        self._minSellPrice = -1
        self._maxBuyPrice = -1
        self._buyPoint = -1
        self._histBuyLim = -1
        self._globalMin = 9999999
        self._globalMax = -1
        self._finBoughtPrice = -1
        self._finSoldPrice = -1

    def _print_current_state(self, lastPrice):
        thisTime = g_get_time()
        if self._globalMin == 9999999:
            printGlobalMin = -1
        else:
            printGlobalMin = self._globalMin
        with open("rlData.csv", "a") as myfile:
            myfile.write(
                '{},{},{},{},{},{},{},{},{},{},{},{}'.format(thisTime, lastPrice, self._globalMax, self._minSellPrice, self._maxBuyPrice,
                                                             printGlobalMin, 0, self._buyPoint, self._sellPoint, self._histSellLim,
                                                             self._histBuyLim, lastPrice))
            myfile.write('\n')
        print '{},{},{},{},{},{},{},{},{},{},{},{}'.format(thisTime, lastPrice, self._globalMax, self._minSellPrice, self._maxBuyPrice,
                                                           printGlobalMin, 0, self._buyPoint, self._sellPoint, self._histSellLim,
                                                             self._histBuyLim, lastPrice)

    def _try_to_wake_up(self):
        if g_get_time()>self._activateTime:
            return True
        else:
            return False

    def _reset_this_agent(self):
        # todo: print to finished deals
        global g_profit_till_now
        global g_profit_counter_till_now

        fees = float((float(self._finSoldPrice))*g_dealingAmount)*0.002 + (float(self._finBoughtPrice)*g_dealingAmount)*0.002
        dertyProfit = float(self._finSoldPrice)*g_dealingAmount - float(self._finBoughtPrice)*g_dealingAmount
        tmpProfit = dertyProfit - fees

        g_profit_counter_till_now += 1
        g_profit_till_now += tmpProfit

        with open("allProfits.csv", "a") as myfile:
            myfile.write('{},{},{},{},{}'.format(g_get_time(), self._winPercentage, tmpProfit, g_profit_counter_till_now, g_profit_till_now))
            myfile.write('\n')

        if self._id == 0:
            self._myState = State.GENERIC
        else:
            self._myState = State.SLEEPING
            g_deactivated_agent(self._id)
            self._activateTime = g_get_next_activate_time()
        self._histSellLim = -1
        self._sellPoint = -1
        self._minSellPrice = -1
        self._maxBuyPrice = -1
        self._buyPoint = -1
        self._histBuyLim = -1
        self._globalMin = 9999999
        self._globalMax = -1
        self._finBoughtPrice = -1
        self._finSoldPrice = -1

    def _sell_this_bitcoin(self,price):
        self._finSoldPrice = g_sell_bitcoin(price)
        global g_totalDollarAmount
        global g_myActiveBitcoins
        g_totalDollarAmount = g_totalDollarAmount + (self._finSoldPrice * g_dealingAmount)
        g_myActiveBitcoins = g_myActiveBitcoins - g_dealingAmount
        with open("allDeals.csv", "a") as myfile:
            myfile.write('1,{},{},{},{}'.format(self._id, g_get_time(), self._finSoldPrice, 0))
            myfile.write('\n')

        if self._myState == State.GENERIC_TRYING_TO_SELL:
            #
            self._myState = State.SOLD_FIRST
            return 0
        # if got here then State.BOUGHT_FIRST, this if just to look nicer
        if self._myState == State.TRYING_TO_SELL:
#         todo: add prints to files
            self._reset_this_agent()
            return 0
        # check for error:
        quit()

    def _buy_this_bitcoin(self,price):
        self._finBoughtPrice = g_buy_bitcoin(price)
        global g_totalDollarAmount
        global g_myActiveBitcoins
        g_totalDollarAmount = g_totalDollarAmount - (self._finSoldPrice * g_dealingAmount)
        g_myActiveBitcoins = g_myActiveBitcoins + g_dealingAmount

        with open("allDeals.csv", "a") as myfile:
            myfile.write('0,{},{},{},{}'.format(self._id, g_get_time(), self._finBoughtPrice, 0))
            myfile.write('\n')

        if self._myState == State.GENERIC_TRYING_TO_BUY:
            #         todo: add prints to files
            self._myState = State.BOUGHT_FIRST
            return 0
        # if got here then State.BOUGHT_FIRST, this if just to look nicer
        if self._myState == State.TRYING_TO_BUY:
            #         todo: add prints to files
            self._reset_this_agent()
            return 0
        # check for error:
        quit()

    def _search_for_sell_point(self, price):
        if price > self._globalMax:
            self._globalMax = price
            self._sellPoint = self._minSellPrice + (self._globalMax - self._minSellPrice) * 0.5
            return 0
        if (price < self._sellPoint) or (g_get_time() > self._gotPastHisteresisTime + g_secs_to_defualt_sellOrBuy):
            self._sell_this_bitcoin(price) # here all the decision on states and resets will be
            self._maxBuyPrice = price * (0.998 * 0.998) / self._winPercentage
            self._histBuyLim = price * (0.998 * 0.998) / (self._winPercentage + 0.005)
            self._sellPoint = -1
            self._minSellPrice = -1

            return 1
        return 0

    def _search_for_buy_point(self, price):

        if price < self._globalMin:
            self._globalMin = price
            self._buyPoint = self._globalMin + (self._maxBuyPrice - self._globalMin) * 0.5
            return 0
        if (price > self._buyPoint) or (g_get_time() > self._gotPastHisteresisTime + g_secs_to_defualt_sellOrBuy):
            self._buy_this_bitcoin(price) # here all the decision on states and resets will be
            self._minSellPrice = self._winPercentage * self._finBoughtPrice / (0.998 * 0.998)
            self._histSellLim = (self._winPercentage + 0.005) * self._finBoughtPrice / (0.998 * 0.998)
            self._buyPoint = -1
            self._maxBuyPrice = -1
            return 1
        return 0

    def _search_for_sell_hist(self, price):
        if price > self._histSellLim:
            self._globalMax = price
            self._sellPoint = self._minSellPrice + (price - self._minSellPrice) * 0.5
            self._myState = State.TRYING_TO_SELL
            self._gotPastHisteresisTime = g_get_time()  # g_secs_to_defualt_sellOrBuy
            return 0

    def _search_for_buy_hist(self, price):
        if price < self._histBuyLim:
            self._globalMin = price
            self._buyPoint = price + (self._maxBuyPrice - price) * 0.5
            self._myState = State.TRYING_TO_BUY
            self._gotPastHisteresisTime = g_get_time()  # g_secs_to_defualt_sellOrBuy
            return 0

    def make_me_money(self, ask, bid ):
        # printing this stat for rlData file
        # print self._myState
        if self._id == 0:
            print self._myState
            self._print_current_state(ask)
        # checking states
        if self._myState == State.SLEEPING:
            if self._try_to_wake_up():
                self._myState = State.GENERIC
                g_activated_agent(self._id)
            else:
                return 0
        if (self._myState == State.TRYING_TO_SELL) or (self._myState == State.GENERIC_TRYING_TO_SELL):
            return self._search_for_sell_point(bid)
        if (self._myState == State.TRYING_TO_BUY) or (self._myState == State.GENERIC_TRYING_TO_BUY):
            return self._search_for_buy_point(ask)

        if self._myState == State.BOUGHT_FIRST:
            return self._search_for_sell_hist(bid)
        if self._myState == State.SOLD_FIRST:
            return self._search_for_buy_hist(ask)

        # checking if got to new high or low
        if ask > self._globalMax:
            self._globalMax = ask
            self._maxBuyPrice = self._globalMax * (0.998*0.998) / self._winPercentage
            self._histBuyLim = self._globalMax * (0.998*0.998) / (self._winPercentage + 0.005)
            return 0

        if bid < self._globalMin:
            self._globalMin = bid
            self._minSellPrice = self._winPercentage * self._globalMin / (0.998 * 0.998)
            self._histSellLim = (self._winPercentage + 0.005) * self._globalMin / (0.998 * 0.998)
            return 0

        if (ask > self._histSellLim) and (ask > g_under_this_you_should_not_sell):

            if (g_myActiveBitcoins > g_dealingAmount*2):
                print "NO WAYYYYYYYYYY"
                print g_myActiveBitcoins
                print g_dealingAmount
                self._go_to_sleep()
                return
            print 'g_under_this_you_should_not_sell: {},bid: {},ask: {},{}'.format(g_under_this_you_should_not_sell, bid, ask)
            self._histSellLim = -1
            self._maxBuyPrice = -1
            self._histBuyLim = -1
            self._myState = State.GENERIC_TRYING_TO_SELL
            self._sellPoint = self._minSellPrice + (ask - self._minSellPrice) * 0.5
            self._gotPastHisteresisTime = g_get_time()  # g_secs_to_defualt_sellOrBuy
            return 0

        if (bid < self._histBuyLim) and (bid < g_over_this_you_should_not_buy):
            if (g_totalDollarAmount <= g_dealingAmountInDollar*2):
                print "WOW WAYYYYYYYYYY"
                print g_totalDollarAmount
                print g_dealingAmountInDollar
                self._go_to_sleep()
                return
            print 'g_over_this_you_should_not_buy: {},bid: {},ask: {},{}'.format(g_over_this_you_should_not_buy, bid, ask)

            self._histBuyLim = -1
            self._minSellPrice = -1
            self._histSellLim = -1
            self._myState = State.GENERIC_TRYING_TO_BUY
            self._buyPoint = ask + (self._maxBuyPrice - ask) * 0.5

            self._gotPastHisteresisTime = g_get_time()  # g_secs_to_defualt_sellOrBuy
            return 0






winPre = (1.0001)
# activeTrades = [ActualTrader(this_id=count, win_percentage=winPre) for count in xrange(g_numberOfAgents)]
# g_numberOfAgents = 1
# activeTrades = [ActualTrader(this_id=count, win_percentage=winPre) for count in xrange(g_numberOfAgents)]
activeTrades = [ActualTrader(this_id=count, win_percentage=uniform(1.000,1.003)) for count in xrange(g_numberOfAgents)]



while True:
    time.sleep(5)

    print g_over_this_you_should_not_buy
    print g_under_this_you_should_not_sell
    print g_numberOfAgents
    print g_activeAgents

    print g_myActiveBitcoins
    print g_dealingAmount
    print g_totalDollarAmount
    print g_dealingAmountInDollar

    thisTime = int(g_get_time())






    try:
        ans = orderbook(symbol='btcusd')
        ask = float(ans['asks'][0]['price'])
        bid = float(ans['bids'][0]['price'])
        print ask
        print bid
        # lastPrice = float(trades()[0]['price'])
    except Exception as ex:
        print("Caught exception {}".format(ex))
        print ans
        time.sleep(60)
        continue

    #on drugs we update every 30 mins
    if g_last_history_scan + 60 * 30 < thisTime:
        get_up_down_percentile()
        g_last_history_scan = thisTime
        update_number_of_agents(ask)

    for agentId in xrange(len(activeTrades)):
        tmp = activeTrades[agentId].make_me_money(ask, bid)













