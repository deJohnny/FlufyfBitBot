import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import datetime

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    graph_data = open('rlData.csv','r').read()
    lines = graph_data.split('\n')
    xs = []
    avg = []
    minSell = []
    maxBuy = []
    sellPoint = []
    buyPoint = []

    upHisteresis = []
    downHisteresis = []

    realPrice = []
    for line in lines:
        if len(line) > 1:
            x, y1, y2, y3, y4, y5, y6, buyLimit, sellLimit, upH, downH, rlPrice = line.split(',')
            xs.append(float(x))
            avg.append(float(y1))
            minSell.append(float(y3))
            maxBuy.append(float(y4))

            sellPoint.append(float(sellLimit))

            buyPoint.append(float(buyLimit))
            upHisteresis.append(float(upH))
            downHisteresis.append(float(downH))
            realPrice.append(float(rlPrice))

    ax1.clear()

    xs = np.array(xs)
    # ticks = xst.astype('datetime64[s]').tolist()
    # plt.plot(ticks, values)


    minSell = np.array(minSell)
    avg = np.array(avg)
    maxBuy = np.array(maxBuy)
    upHisteresis = np.array(upHisteresis)
    downHisteresis = np.array(downHisteresis)
    buyPoint = np.array(buyPoint)
    sellPoint = np.array(sellPoint)
    realPrice = np.array(realPrice)


    ## get deals info
    buyTimeArr = []
    buyPriceArr = []
    sellTimeArr = []
    sellPriceArr = []
    allProfits = []
    graph_data = open('allDeals.csv', 'r').read()
    lines = graph_data.split('\n')
    for line in lines:
        if len(line) > 1:
            #myfile.write('0,{},{},{},0'.format(self.id, toPrint[0], thisInput))
            # [ 0=buy 1=sell , id , time , price
            bORs, id, time, price, profit = line.split(',')

            if int(bORs) == 0: #buy
                buyTimeArr.append(int(round(float(time))))
                buyPriceArr.append((float(price)))
            if int(bORs) == 1: #sell
                sellTimeArr.append(int(round(float(time))))
                sellPriceArr.append((float(price)))
                allProfits.append(float(profit))
    buyTimeArr = np.array(buyTimeArr)
    buyPriceArr = np.array(buyPriceArr)
    sellTimeArr = np.array(sellTimeArr)
    sellPriceArr = np.array(sellPriceArr)

    # if max(realPrice) > 0:
    #     xst = xs[realPrice > 0]
    #     ticks = xst.astype('datetime64[s]').tolist()
    #     ax1.plot(ticks, realPrice[realPrice > 0],'o', label='Real data')
    if max(avg) > 0:
        xst=xs[avg>0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, avg[avg>0], label='Real data', linewidth=2.0)
    if max(minSell) > 0:
        xst = xs[minSell > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, minSell[minSell > 0],'o', label='minSell')
    if max(maxBuy) > 0:
        xst = xs[maxBuy > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, maxBuy[maxBuy>0],'o', label='maxBuy')
    if max(upHisteresis) > 0:
        xst = xs[upHisteresis > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, upHisteresis[upHisteresis>0],'o', label='upHisteresis')
    if max(downHisteresis) > 0:
        xst = xs[downHisteresis > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, downHisteresis[downHisteresis>0],'o', label='downHisteresis')
    if max(buyPoint) > 0:
        xst = xs[buyPoint > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, buyPoint[buyPoint>0],'o', label='buyPoint')
    if max(sellPoint) > 0:
        xst = xs[sellPoint > 0]
        ticks = xst.astype('datetime64[s]').tolist()
        ax1.plot(ticks, sellPoint[sellPoint>0],'o', label='sellPoint')


    if len(buyTimeArr)>0:
        ticks = buyTimeArr.astype('datetime64[s]').tolist()
        ax1.plot(ticks, buyPriceArr, 'r^',markersize= 10, label='BOUGHT')
    if len(sellTimeArr)>0:
        ticks = sellTimeArr.astype('datetime64[s]').tolist()
        ax1.plot(ticks, sellPriceArr, 'g^',markersize= 10, label='SOLD')


    # plt.ylim(14500, 16500)
    plt.legend(loc='upper left')


ani = animation.FuncAnimation(fig,animate,interval=1000)
plt.subplots_adjust(bottom=0.2)
plt.xticks( rotation=25 )

plt.show()
# ax1.xaxis.set_major_formatter(xfmt)


