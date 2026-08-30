import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

FUNDS = {
    "fund1": {
        "name": "安聯收益成長基金-AM穩定月收類股(美元)",
        "dj_id": "ACAA17-03B5",
    },
    "fund2": {
        "name": "瀚亞多重收益優化組合基金B類型(美元)",
        "dj_id": "FLZ36-E962",
    },
    "fund3": {
        "name": "聯博-美國成長基金AP(總報酬月配)級別美元",
        "dj_id": "FLZ06-F027",
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_fund_data(fund_id):
    url = f"https://www.moneydj.com/funddj/yp/yp011001.djhtm?a={fund_id}"
    res = requests.get(url, headers=HEADERS, timeout=15)
    res.encoding = 'big5'
    soup = BeautifulSoup(res.text, 'html.parser')

    nav = None
    nav_tag = soup.find(id="lbNav") or soup.find("span", {"class": "Price"})
    if nav_tag:
        nav = float(re.sub(r'[^\d.]', '', nav_tag.text))

    div_url = f"https://www.moneydj.com/funddj/yp/yp013003.djhtm?a={fund_id}"
    res_div = requests.get(div_url, headers=HEADERS, timeout=15)
    res_div.encoding = 'big5'
    soup_div = BeautifulSoup(res_div.text, 'html.parser')

    dividend = None
    table = soup_div.find("table", {"class": "datalist"})
    if table:
        rows = table.find_all("tr")
        if len(rows) > 1:
            cols = rows[1].find_all("td")
            if len(cols) >= 3:
                dividend = float(cols[2].text.strip())

    annual_yield = 0.0
    if nav and dividend:
        annual_yield = round(((dividend * 12) / nav) * 100, 2)

    return {
        "nav": nav,
        "dividend": dividend,
        "annual_yield": annual_yield
    }

def main():
    result = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "funds": {}
    }

    for key, info in FUNDS.items():
        try:
            data = get_fund_data(info["dj_id"])
            result["funds"][key] = {
                "name": info["name"],
                "nav": data["nav"],
                "dividend": data["dividend"],
                "annual_yield": data["annual_yield"]
            }
        except Exception as e:
            result["funds"][key] = {"name": info["name"], "annual_yield": 7.5}

    with open("fund_rates.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
