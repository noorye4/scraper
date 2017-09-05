from bs4 import BeautifulSoup
import urllib
import requests
import os
import json
import time
import re


target_url = "https://www.asus.com/OfficialSiteAPI.asmx/GetModelResults?WebsiteId=1&ProductLevel2Id=1849&FiltersCategory=2542&Filters=&Sort=3&PageNumber=1&PageSize=999"


response = requests.get(target_url)
json_data = json.loads(response.text)
# print data

products = json_data["Result"]["Obj"]
# print url_list

index = 0
for product in products:
    # print product["Url"]
    # # print i["Url"]
    product = product["Url"].replace("//","")
    firmware_url = "http://" + product + "HelpDesk_BIOS/"
    # print firmware_url
    response = requests.get(firmware_url)
    if response.status_code == 200:
        r = re.findall(r'pdhashid:...................', response.text) 
        model = product.rsplit('/', 1)[0]
        model = model.split("/")[-1]

        # model = 

        pdhashid = r[0].split(":")[1]
        pdhashid = pdhashid[2:-1]

        download_link = "https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=global&pdhashedid={p_str}&model={p_model}&callback=supportpdpage".format(p_str=pdhashid,p_model=model)

        response = requests.get(download_link)
        if response.status_code == 200:
            match = re.search("No Data Found",response.text)
            if match:
                pass
            else:
                s = response.text.replace("supportpdpage","")
                s = s.replace("(","")
                s = s.replace(")","")
                download_json = json.loads(s)
                objs = download_json["Result"]["Obj"][0]["Files"]
                for obj in objs:

                    print  obj["Title"]
                    print  obj["Version"]
                    print  obj["FileSize"]
                    print  obj["ReleaseDate"]
                    # print  obj["Description"]

                    print  obj["DownloadUrl"]["Global"]
                    index += 1
                print index,"-"*20



