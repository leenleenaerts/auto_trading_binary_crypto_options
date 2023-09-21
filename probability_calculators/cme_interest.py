# import modules
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def calculate_interest_rate_probability(date_string, lower, upper):

    # variables
    url = 'https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html'
    chromedriver_path = Service(r'chromedriver.exe')


    # adding chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('log-level=1')


    # start chrome
    driver = Chrome(service=chromedriver_path, options=options)
    driver.get(url)

    # scrap the data
    iframe = driver.find_element(By.CLASS_NAME, 'cmeIframe')
    driver.switch_to.frame(iframe)

    date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="MainContent_pnlContainer"]/div[3]/div/div/div/div[1]/table/tbody/tr/td[1]/table/tbody/tr[3]/td[1]')))
    if date_string not in date.text:
        print(f"Not the correct date! Found date is: {date.text}")
        quit()

    ranges = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//table//tr[@class=""]/td[@class="center"]')))
    headings = []
    for r in ranges:
        headings.append(r.text.split()[0])

    highlights = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'highlight')))
    result = []
    for highlight in highlights:
        if highlight.text != '':
            result.append(highlight.text)

    # clsoe chrome
    driver.quit()

    for i in range(len(headings)):
        if headings[i].split("-")[0] == str(lower) and headings[i].split("-")[1] == str(upper):
            prob = float(result[i].replace("%", "")) / 100
            print(prob)
            return prob

    print("No data found for this range")
    quit()


# Main function
if __name__ == "__main__":
    prob = calculate_interest_rate_probability("Sep 2023", 550, 575)
    print(prob)


