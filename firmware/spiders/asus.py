from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urlparse
import json
import requests
import time
import requests
import os
import json
import time
import re


class AsusSpider(Spider):
    name = "asus"
    region = "en"
    allowed_domains = ["asus.com"]
    start_urls = ["https://www.asus.com/OfficialSiteAPI.asmx/GetModelResults?WebsiteId=1&ProductLevel2Id=1849&FiltersCategory=2542&Filters=&Sort=3&PageNumber=1&PageSize=999"]

    visited = []

    def parse(self, response):
        json_data = json.loads(response.text)
        products = json_data["Result"]["Obj"]

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

                            product = obj["Title"]
                            vendor = "asus"
                            sdk = "None"
                            version = obj["Version"]
                            date = obj["ReleaseDate"]
                            description = obj["Description"]
                            url = obj["DownloadUrl"]["Global"]

                            item = FirmwareLoader(item=FirmwareImage(),
                                                response=response, date_fmt=["%Y/%m/%d"])
                            item.add_value("version", version)
                            item.add_value("date", date)
                            item.add_value("description",description )
                            item.add_value("url", url)
                            item.add_value("sdk", sdk)
                            item.add_value("product", product)
                            item.add_value("vendor", vendor)
                            yield item.load_item()









                            index += 1
                        # print index,"-"*20


























        # if "cid" not in response.meta:
        #     for category in response.xpath("//div[@class='product-category']//a/@l1_id").extract():
        #         yield Request(
        #             url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s" % (self.region, category)),
        #             meta={"cid": category},
        #             headers={"Referer": response.url,
        #                      "X-Requested-With": "XMLHttpRequest"},
        #             callback=self.parse)
        #
        # elif "sid" not in response.meta:
        #     for series in response.xpath("//table/id/text()").extract():
        #         yield Request(
        #             url=urlparse.urljoin(response.url, "/support/utilities/GetProducts.aspx?ln=%s&p=%s&s=%s" % (self.region, response.meta["cid"], series)),
        #             meta={"cid": response.meta["cid"], "sid": series},
        #             headers={"Referer": response.url,
        #                      "X-Requested-With": "XMLHttpRequest"},
        #             callback=self.parse)
        #
        # elif "product" not in response.meta:
        #     for prod in response.xpath("//table"):
        #         pid = prod.xpath("./l3_id/text()").extract()[0]
        #         product = prod.xpath("./m_name/text()").extract()[0]
        #         mid = prod.xpath("./m_id/text()").extract()[0]
        #
        #         # choose "Others" = 8
        #         yield Request(
        #             url=urlparse.urljoin(response.url, "/support/Download/%s/%s/%s/%s/%d" % (response.meta["cid"], response.meta["sid"], pid, mid, 8)),
        #             meta={"product": product},
        #             headers={"Referer": response.url,
        #                      "X-Requested-With": "XMLHttpRequest"},
        #             callback=self.parse_product)





    def parse_product(self, response):
        # types: firmware = 20, gpl source = 30, bios = 3
        for entry in response.xpath(
                "//div[@id='div_type_20']/div[@id='download-os-answer-table']"):
            item = FirmwareLoader(item=FirmwareImage(),
                                  response=response, date_fmt=["%Y/%m/%d"])

            version = FirmwareLoader.find_version_period(
                entry.xpath("./p//text()").extract())
            gpl = None

            # grab first download link (e.g. DLM instead of global or p2p)
            href = entry.xpath("./table//tr[3]//a/@href").extract()[0]

            # attempt to find matching source code entry
            if version:
                for source in response.xpath("//div[@id='div_type_30']/div[@id='download-os-answer-table']"):
                    if version in "".join(source.xpath("./p//text()").extract()):
                        gpl = source.xpath("./table//tr[3]//a/@href").extract()[0]

            item.add_value("version", version)
            item.add_value("date", item.find_date(entry.xpath("./table//tr[2]/td[1]//text()").extract()))
            item.add_value("description", " ".join(entry.xpath("./table//tr[1]//td[1]//text()").extract()))
            item.add_value("url", href)
            item.add_value("sdk", gpl)
            item.add_value("product", response.meta["product"])
            item.add_value("vendor", self.name)
            yield item.load_item()

