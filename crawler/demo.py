import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


options = Options()
# options.add_argument("--headless")


driver = webdriver.Chrome(options=options)


driver.get("http://zwfw.hubei.gov.cn/webview/fw/grfw.html")
assert "湖北政务服务网" == driver.title

while True:
    subjects = driver.find_elements(By.CLASS_NAME, "mulu_item")
    for subject in subjects:
        subject.click()
        time.sleep(0.5)
        for item in subject.find_elements(By.CLASS_NAME, "ywblxItem"):
            title = subject.find_element(By.CLASS_NAME, "title_text").text
            addition = subject.find_element(By.CLASS_NAME, "title_add").text
            print(title, addition, item.text)

    try:
        downpage = driver.find_element(By.CLASS_NAME, "downPage")
    except:
        break

    downpage.click()
    time.sleep(0.5)

driver.close()
