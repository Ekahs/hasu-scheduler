from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import chromedriver_binary
from bs4 import BeautifulSoup

import requests
import json
import os

SLACK_URL=os.environ["SLACK_URL"]

TARGET_DAYS = [
  '2020/02/06',
  '2020/02/07',
  '2020/02/08',
  '2020/02/09',
  '2020/02/10',
  ]
TARGET_MONTH = "2月"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
DRIVER = webdriver.Chrome(options=options)

def get_page_source(): 
  DRIVER.get('http://hnd-rsv.aeif.or.jp/airport2/app/toppage')
  DRIVER.find_element_by_id("cal10_next").click()
  WebDriverWait(DRIVER, 15).until(expected_conditions.text_to_be_present_in_element((By.ID, "cal10_title"), TARGET_MONTH))
  return DRIVER.page_source
  
def check(td):
  if len(td['class']) <= 0:
    return False
  
  check_day = td['id'][4:]
  status = td['class'][0]
  
  if status == 'full':
    return False
  
  for target_day in TARGET_DAYS:
    if check_day == target_day:
      return True
  
  return False
  
def send_slack(text):
  if text == "":
    return
  
  payload = {
    "text": "下記日程が空いてます。\r\n" + text,
  }
  
  data = json.dumps(payload)
  requests.post(SLACK_URL, data)
  
def main():
  soup = BeautifulSoup(get_page_source(), "lxml")

  table = soup.find("table", id="cal10")

  send_text = ""
  for tr in table.find_all("tr")[1:]:
    for td in tr.find_all("td"):
      if check(td):
        send_text = send_text + td['id'][4:] + "\r\n"
        
  send_slack(send_text)
        
if __name__ == "__main__":
    try: 
      main()
    except Exception as e:
        print(e)
    finally:
        DRIVER.quit()
    
