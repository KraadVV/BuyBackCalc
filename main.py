from prettytable import PrettyTable
import tkinter
import multiprocessing
import csv
import requests

# contract = [itemname, itemquantity, itemno, buy, sell, sbm]

# 바이셀 가격 받아오기
def buySellPrice(contract):
    query = "https://esi.evetech.net/latest/markets/10000002/orders/"
    for i in range(len(contract)):

        #buy, sell 초기화

        buyPrices = []
        sellPrices = []

        # id값을 기반으로 GET request
        idx = 1
        data = {'datasource': 'tranquility',
                'order_type': 'all',
                'page': idx,
                'type_id': contract[2]}

        # ESI request
        response = requests.get(url=query, params=data)

        # print(response)

        # 바이, 셀 가격 모으는 부분

        jsonObj = response.json()

        # print(jsonObj)
        for j in range(len(jsonObj)):
            if jsonObj[j].get("system_id") == 30000142:
                if jsonObj[j].get("is_buy_order") == False:
                    sellPrices.append(jsonObj[j].get("price"))
                if jsonObj[j].get("is_buy_order") == True:
                    buyPrices.append(jsonObj[j].get("price"))

        buyPrices.sort(reverse=True)  # 내림차순
        sellPrices.sort()  # 오름차순

        # 셀가 1번째 값과 바이가 1번째 값을 더한 뒤 2로 나눈다. 이 값을 '셀바중' 값에 넣는다.
        contract.append(buyPrices[0])
        contract.append(sellPrices[0])

        medianPrice = (buyPrices[0]+sellPrices[0]) / 2
        contract.append(medianPrice)

        return contract

# 유저 스트링을 인식, 이름과 수량을 이중 리스트로 빼낸다.
def recogContract(userString):
    contract = []  # [itemName, quantity]
    userString = userString.split("\n")
    for rows in userString:
        rows = rows.split("\t")
        appendArray = [rows[0], int(rows[1])]
        contract.append(appendArray)
    #contract.append(["","","","","","",""])
    #print(contract)
    return contract

def receipt(contract, totalPrice):
    t = PrettyTable(['itemName', 'quantity', 'medianPrice', 'Total'])
    for obj in contract:
        t.add_row([obj[0], obj[1], obj[5], obj[6]])
    t.add_row(["-", "-", "-", "-"])
    t.add_row(["Total", "", "", totalPrice])
    return(t)

def processClick():
    userInput = txt.get()

    list = recogContract(userInput)
    list = idExtraction(list)
    list, total = fetchTable(list)
    #messagebox.showinfo("receipt", receipt(list, total))

    output_entry_value.set(receipt(list, total))



# 기존에 가지고 있던 CSV 파일에서 해당 물건의 ID값을 추출한다
def idExtraction(contract):
    for i in range(len(contract)):
        # item_name 전처리
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

        # idTable 열기, 아이템 이름에 맞는 아이템 ID 가져와서 append
    with open('typeids.csv', encoding='utf8') as typeID:
        idTable = csv.reader(typeID)

        for row in idTable:
            for i in range(len(contract)):
                if row[1] == contract[i][0]:
                    item_id = row[0]
                    contract[i].append(item_id)
                    continue

    return contract

#ESI 접속하여 셀바이 가격 받아오기
def fetchTable(contract):

    # 멀티프로세스 객체 형성
    idx = 0

    pool = multiprocessing.Pool(processes=4)
    contract = pool.map(buySellPrice, contract)
    pool.close()
    pool.join()


    totalPrice = 0
    for i in range(len(contract)):
        itemPrice = contract[i][5]*contract[i][1]
        contract[i].append(itemPrice)

        totalPrice += itemPrice

    return contract, totalPrice

def copyClick():
    root.clipboard_clear()
    root.clipboard_append(txt2.get())


if __name__ == '__main__':
    #tkinter 기본

    root = tkinter.Tk()
    root.title("Jita Median Price calculator")
    root.geometry("720x480")
    root.resizable(0,0)

    lbl = tkinter.Label(root, text = "paste your contract here")
    lbl.grid(row=0, column=0, padx=10, pady=10, ipadx=20, ipady=10)

    lbl2 = tkinter.Label(root, text = "Receipt")
    lbl2.grid(row=0, column=1, padx=10, pady=10, ipadx=20, ipady=10)

    process_value = tkinter.StringVar()
    process = tkinter.Label(root, textvariable=process_value)

    output_entry_value = tkinter.StringVar()

    txt = tkinter.Entry(root)
    txt.grid(row=1, column=0, padx=10, pady=10, ipadx=60, ipady=35)

    txt2 = tkinter.Entry(root, textvariable=output_entry_value)
    txt2.grid(row=1, column=1, padx=10, pady=10, ipadx=60, ipady=35)

    btn = tkinter.Button(root, text="Start Calculation", command=processClick)
    btn.grid(row=2, column=0, padx=10, pady=10, ipadx=20, ipady=10)

    copybtn = tkinter.Button(root, text = "copy to clipboard", command=copyClick)
    copybtn.grid(row=2,column=1, padx=10, pady=10, ipadx=20, ipady=10)

    root.mainloop()





#출력부


    #https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=all&page=1&type_id=2621 # 2621 = 인페르노 퓨리 크루즈
    #- 상기 url을 바탕으로 XML 형태를 받는다
    #셀가와 바이가로 나누어 정렬한다.
    #셀가는 오름차순, 바이가는 내림차순

    #계속 그 다음 행에 대해 실행한다.
    #더 이상 실행할 행이 없으면 다음과 같이 프린트 후 종료한다.

