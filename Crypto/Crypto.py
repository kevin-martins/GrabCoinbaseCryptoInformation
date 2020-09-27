import time
import datetime
import winsound
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from win10toast import ToastNotifier

#Send notification on WhatsApp
def send_notification(client, notifier, action, msg):
    notifier.show_toast(action, msg)
    #client.messages.create(body=f'Buy some!\nBTC: {lastPrice} -> {newPrice}', from_='whatsapp:+14155238886', to='whatsapp:+33631545589')

#Print crypto price if it seems valuable to buy or sell
def print_crypto(key, value, action, color):
    print(f'\n{color}*******************************************************\033[0m')
    print(f'{color}*\033[0mShould {action} Some {key}:')
    print(f"{color}*\033[0m\tPrice: {value['Price1']}€ -> {value['Price2']}€ -> {value['Price3']}€ -> {value['Price4']}€ -> {value['Price5']}€")
    print(f"{color}*\033[0m\tFrom {value['Price1']}€ to {value['Price5']}€, diff={value['Price5']-value['Price1']}")
    print(f"{color}*\033[0m\tTrend: {value['lastTrend']}% -> {value['newTrend']}%")
    print(f'{color}*******************************************************\033[0m')

#Move each price one step to the left
def organise_crypto(crypto):
    crypto['Price1'] = crypto['Price2']
    crypto['Price2'] = crypto['Price3']
    crypto['Price3'] = crypto['Price4']
    crypto['Price4'] = crypto['Price5']
    crypto['lastTrend'] = crypto['newTrend']
    return crypto

#Add to a tab each crypto and its price
def get_crypto_price(url, crypto, creation):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    source = soup.findAll('tr')
    #The range is use to take in consideration more cryptocurrency
    for i in range(7, 50):
        try:
            int(str(source).split('TextElement')[i].split('\">')[1].split('<')[0])
            money = str(source).split('TextElement')[i+1].split('\">')[1].split('<')[0]
            if creation:
                crypto[money] = {'Price1':0.0, 'Price2':0.0, 'Price3':0.0, 'Price4':0.0, 'Price5':0.0, 'lastTrend':0.0, 'newTrend':0.0}
            else:
                crypto[money] = organise_crypto(crypto[money])
            crypto[money]['Price5'] = float(str(source).split('TextElement')[i+3].split('\">')[1].split('<')[0].split('€')[1].replace(',', ''))
            crypto[money]['newTrend'] = float(str(source).split('TextElement')[i+4].split('\">')[1].split('<')[0].split('%')[0])
        except:
            next
    return crypto

#If the current crypto is growing
def increasing(key, value):
    if (value['Price1'] < value['Price2'] and value['Price1'] < value['Price3'] and
     value['Price1'] < value['Price4'] and value['Price1'] < value['Price5'] and
     value['lastTrend'] > value['newTrend'] and value['newTrend'] < -5):
        print(datetime.datetime.now().strftime("%H:%M:%S"))
        print_crypto(key, value, 'Buy', '\033[32m')
        #send_notification(client, notifier, 'BUY', f"{key}: {value['lastPrice']} -> {value['newPrice']}")
    else:
        return False
    return True

#If the current crypto is decreasing
def decreasing(key, value):
    if (value['Price1'] > value['Price2'] and value['Price1'] > value['Price3'] and
     value['Price1'] > value['Price4'] and value['Price1'] > value['Price5'] and
     value['newTrend'] > value['lastTrend'] and value['newTrend'] > 5):
        print(datetime.datetime.now().strftime("%H:%M:%S"))
        print_crypto(key, value, 'Sell', '\033[31m')
        #send_notification(client, notifier, 'SELL', f"{key}: {value['lastPrice']} -> {value['newPrice']}")
    else:
        return False
    return True


#Check both decreasement and increasement
def check_trend(client, notifier, crypto, loop):
    buyState = False
    sellState = False
    state = False 
    for key, value in crypto.items():
        buyState = increasing(key, value)
        sellState = decreasing(key, value)
        if buyState and sellState:
            state = False
        else:
            state = True
    if state:
        #informe the user that the programme is running and how many loop it did.
        print('No need to buy or sell, wait till the second loop. Current loop: ', loop)
    return crypto

    # Decreases
        #winsound.Beep(2000, 1000)
        #winsound.Beep(6000, 1000)
        #send_notification(client, notifier, 'SELL', f"BTC: {lastPrice} -> {newPrice}")


def main():
    url = 'https://www.coinbase.com/price/'
    crypto = {}
    creation = True
    client = Client('AC596a0a7ee0cc9c9e5848ee8deb7e50ce', '511ad17692f74747208a6fb1905dabbb')
    notifier = ToastNotifier()
    print(datetime.datetime.now().strftime("%A, %B %d, %Y"))
    loop = 1
    while True:
        crypto = check_trend(client, notifier, get_crypto_price(url, crypto, creation), loop)
        creation = False
        #Time between each calculation, here 3mins
        time.sleep(3*60)
        loop+=1

if __name__=='__main__':
    main()
