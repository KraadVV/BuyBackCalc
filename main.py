from tabulate import tabulate
import json
import csv
import requests
import json


if __name__ == '__main__':
    # 유저 스트링을 인식, 이름과 수량을 이중 리스트로 빼낸다.
    contract = []  # [itemName, quantity]
    with open('contract example', encoding='utf8') as userString:
        for rows in userString:
            rows = rows.split("\t")
            appendArray = [rows[0], int(rows[1])]
            contract.append(appendArray)
    #contract.append(["","","","","","",""])
    #print(contract)


    # 기존에 가지고 있던 CSV 파일에서 해당 물건의 ID값을 추출한다

    query = "https://esi.evetech.net/latest/markets/10000002/orders/"

    #contract = [itemname, itemquantity, itemno, buy, sell, sbm]
    for i in range(len(contract)):
        #item_name 전처리
        item_name = contract[i][0].replace('*', '')
        try:
            if item_name[0] == " ":
                item_name = item_name[1:]
        except:
            pass

        contract[i][0] = item_name

        # 중복 제거
    for i in range(len(contract)):
        try:
            while contract[i][0] == contract[i + 1][0]:
                contract[i][1] += contract[i + 1][1]
                del contract[i + 1]
        except:
            pass

        #idTable 열기, 아이템 이름에 맞는 아이템 ID 가져와서 append
    with open('typeids.csv', encoding='utf8') as typeID:
        idTable = csv.reader(typeID)


        for row in idTable:
            for i in range(len(contract)):
                if row[1] == contract[i][0]:
                    item_id = row[0]
                    contract[i].append(item_id)
                    continue
    for i in range(len(contract)):
        print("processing %d out of %d items" %(i+1, len(contract)))


        #id값을 기반으로 GET request
        idx = 1
        data = {'datasource': 'tranquility',
                'order_type': 'all',
                'page': idx,
                'type_id': item_id}

        #ESI request
        response = requests.get(url=query, params=data)


        #print(response)

        #바이, 셀 가격 모으는 부분
        buyPrices = []
        sellPrices = []
        jsonObj = response.json()

        #print(jsonObj)
        for j in range(len(jsonObj)):
            if jsonObj[j].get("system_id") == 30000142:
                if jsonObj[j].get("is_buy_order") == False:
                    sellPrices.append(jsonObj[j].get("price"))
                if jsonObj[j].get("is_buy_order") == True:
                    buyPrices.append(jsonObj[j].get("price"))

        buyPrices.sort(reverse=True) #내림차순
        sellPrices.sort() #오름차순

        # 셀가 1번째 값과 바이가 1번째 값을 더한 뒤 2로 나눈다. 이 값을 '셀바중' 값에 넣는다.
        contract[i].append(buyPrices[0])
        contract[i].append(sellPrices[0])
        contract[i].append((buyPrices[0]+sellPrices[0])/2)


    totalPrice = 0
    for i in range(len(contract)):
        itemPrice = contract[i][5]*contract[i][1]
        contract[i].append(itemPrice)

        totalPrice += itemPrice


    print("========Receipt========")
    print(tabulate(contract, headers=["itemName", "quantity","itemNo", "BuyPrice", "SellPrice", "medianPrice", "Total"]))
    print("=======================")
    print("total %d isk" %totalPrice)


    #https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=all&page=1&type_id=2621 # 2621 = 인페르노 퓨리 크루즈
    #- 상기 url을 바탕으로 XML 형태를 받는다
    #셀가와 바이가로 나누어 정렬한다.
    #셀가는 오름차순, 바이가는 내림차순

    #계속 그 다음 행에 대해 실행한다.
    #더 이상 실행할 행이 없으면 다음과 같이 프린트 후 종료한다.

