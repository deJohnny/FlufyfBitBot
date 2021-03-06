# Python implementation. Written by jndok - 2014. Distributed under GNU/GPL v3 (http://opensource.org/licenses/GPL-3.0). [v. 0.0.1-4]
# report ANY bug @ me@jndok.net

import requests
import json
import base64
import hmac
import hashlib
import time

from decimal import Decimal

__all__ = ['ticker', 'today', 'orderbook', 'lendbook', 'stats', 'trades', 'lends', 'symbols', 'place_order', 'delete_order', 'status_order', 'active_orders', 'active_positions', 'place_offer', 'cancel_offer', 'status_offer', 'active_offers', 'past_trades', 'balances']

URL = "https://api.bitfinex.com/v1"

API_KEY = "WdrFkRoKO3kIDaJeIvoVFzPP6wzSFT0cnUAAn8JAIk8" # put your API private key here.
API_SECRET = "5l720u3OmolY2qExsyy8D33lHy6qnfGPIIjOhdB5gI5" # put your API secret here.

# unauthenticated


def ticker(symbol='btcusd'): # gets the innermost bid and asks and information on the most recent trade.

	r = requests.get(URL + "/pubticker/" + symbol, verify=False) # <== UPDATED TO LATEST VERSION OF BFX!
	rep = r.json()

	try:
		rep['last_price']
	except KeyError:
		return rep['message']

	return rep

def stats(symbol='btcusd'): # Various statistics about the requested pairs.

	r = requests.get(URL + "/stats/" + symbol, verify=False) # <== UPDATED TO LATEST VERSION OF BFX!
	rep = r.json()

	try:
		rep['volume']
	except KeyError:
		return rep['message']

	return rep

def today(symbol='btcusd'): # today's low, high and volume.

	r = requests.get(URL + "/today/" + symbol, verify=False)
	rep = r.json()

	try:
		rep['volume']
	except KeyError:
		return rep['message']

	return rep

def orderbook(symbol='btcusd'): # get the full order book.

	r = requests.get(URL + "/book/" + symbol, verify=False)
	rep = r.json()

	return rep

def lendbook(currency='btc'): # get the full lend book.

	r = requests.get(URL + "/lendbook/" + currency, verify=False)
	rep = r.json()

	return rep

def trades(symbol='btcusd'): # get a list of the most recent trades for the given symbol.

	r = requests.get(URL + "/trades/" + symbol, verify=False)
	rep = r.json()

	return rep

def lends(currency='btc'): # get a list of the most recent lending data for the given currency: total amount lent and rate (in % by 365 days).

	r = requests.get(URL + "/lends/" + currency, verify=False)
	rep = r.json()

	return rep

def symbols(): # get a list of valid symbol IDs.

	r = requests.get(URL + "/symbols", verify=False)
	rep = r.json()

	return rep

# authenticated

def genNonce(): # generates a nonce, used for authentication.
	return str(long(time.time() * 1000000))

def payloadPacker(payload): # packs and signs the payload of the request.

	j = json.dumps(payload)
	data = base64.standard_b64encode(j)

	h = hmac.new(API_SECRET, data, hashlib.sha384)
	signature = h.hexdigest()

	return {
		"X-BFX-APIKEY": API_KEY,
		"X-BFX-SIGNATURE": signature,
		"X-BFX-PAYLOAD": data
	}

def place_order(amount, price, side, ord_type, symbol='btcusd', exchange='all'): # submit a new order.

	payload = {

		"request":"/v1/order/new",
		"nonce":genNonce(),
		"symbol":symbol,
		# "amount":amount,
        "amount": str(amount),
		"price":str(price),
		"exchange":exchange,
		"side":side,
		"type":ord_type

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/order/new", headers=signed_payload, verify=False)
	rep = r.json()

	try:
		rep['order_id']
	except:
		return rep['message']

	return rep

def delete_order(order_id): # cancel an order.

	payload = {

		"request":"/v1/order/cancel",
		"nonce":genNonce(),
		"order_id":order_id

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/order/cancel", headers=signed_payload, verify=False)
	rep = r.json()

	try:
		rep['avg_excution_price']
	except:
		return rep['message']

	return rep

def status_order(order_id): # get the status of an order. Is it active? Was it cancelled? To what extent has it been executed? etc.

	payload = {

		"request":"/v1/order/status",
		"nonce":genNonce(),
		"order_id":order_id

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/order/status", headers=signed_payload, verify=False)
	rep = r.json()

	try:
		rep['avg_excution_price']
	except:
		return rep['message']

	return rep

def active_orders(): # view your active orders.

	payload = {

		"request":"/v1/orders",
		"nonce":genNonce()

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/orders", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def active_positions(): # view your active positions.

	payload = {

		"request":"/v1/positions",
		"nonce":genNonce()

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/positions", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def claim_position(position_id): # Claim a position.

	payload = {

		"request":"/v1/position/claim",
		"nonce":genNonce(),
		"position_id":position_id

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/position/claim", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def past_trades(timestamp, symbol='btcusd'): # view your past trades

	payload = {

		"request":"/v1/mytrades",
		"nonce":genNonce(),
		"symbol":symbol,
		"timestamp":timestamp

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/mytrades", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def place_offer(currency, amount, rate, period, direction):

	payload = {

		"request":"/v1/offer/new",
		"nonce":genNonce(),
		"currency":currency,
		"amount":amount,
		"rate":rate,
		"period":period,
		"direction":direction

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/offer/new", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def cancel_offer(offer_id):

	payload = {

		"request":"/v1/offer/cancel",
		"nonce":genNonce(),
		"offer_id":offer_id

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/offer/cancel", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def status_offer(offer_id):

	payload = {

		"request":"/v1/offer/status",
		"nonce":genNonce(),
		"offer_id":offer_id

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/offer/status", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def active_offers():

	payload = {

		"request":"/v1/offers",
		"nonce":genNonce()

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/offers", headers=signed_payload, verify=False)
	rep = r.json()

	return rep

def balances(): # see your balances.

	payload = {

		"request":"/v1/balances",
		"nonce":genNonce()

	}

	signed_payload = payloadPacker(payload)
	r = requests.post(URL + "/balances", headers=signed_payload, verify=False)
	rep = r.json()

	return rep
# ans=place_order(amount=0.001, price=15500, side='sell', ord_type='limit', symbol='btcusd', exchange='all')
print "hi"