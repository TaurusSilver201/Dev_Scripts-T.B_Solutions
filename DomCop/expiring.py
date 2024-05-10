from selenium import webdriver
import os
import glob
import shutil
import config
import ftplib
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import random

CSV_FILE_PATH = "domains.csv"

URLS = ["https://www.domcop.com/domains?sid=14552",
        "https://www.domcop.com/domains?sid=14554",
        "https://www.domcop.com/domains?sid=14556"]

service = webdriver.ChromeService()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
options.add_argument('log-level=3')
options.add_argument(r'user-data-dir=C:\Users\User3\AppData\Local\Google\Chrome\User Data')
prefs = {"download.default_directory" : r"C:\DomCop\Expiring"}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=service, options=options)

print('.: EXPIRING.BAT :.')

def random_sleep(x, y):
    sleep_time = random.uniform(x, y)
    time.sleep(sleep_time)

def main(driver, url):
    try:
        #access the web page
        driver.get(url)
        random_sleep(5, 10)
        print("accessing web")
        driver.find_element(By.XPATH, '//button[@class="btn btn-primary btn-minier"][3]').click()
        print("export..")
        random_sleep(1, 2)
        driver.find_element(By.LINK_TEXT, 'Select None').click()
        random_sleep(3, 5)
        print("choosing menu..")
        driver.find_element(By.XPATH, '//input[@name="DomainData"]').click()
        random_sleep(1, 2)
        driver.find_element(By.XPATH, '//input[@name="SeomozData"]').click()
        random_sleep(1, 2)
        driver.find_element(By.XPATH, '//input[@name="MajesticData"]').click()
        random_sleep(1, 2)
        driver.find_element(By.XPATH, '//button[@class="btn btn-info"][1]').click()
        random_sleep(2, 5)
        print("waiting to download file...")

        try:
            random_sleep(10, 15)
            link = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,'//tr[2]/td[8]/a[@href]')))
            link.click()
            random_sleep(5, 10)
            print("download success...")
        except:
            print('loading more... wait!')
            random_sleep(10, 15)
            link = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH,'//tr[2]/td[8]/a[@href]')))
            link.click()
            random_sleep(5, 10)
            print("download success...")

        # link = None
        # while not link:
        #     try:
        #         time.sleep(20)
        #         link = driver.find_element(By.XPATH, '//tr[2]/td[8]/a[@href]').click()
        #         link = 'done'
        #         print("download success...")
        #     except NoSuchElementException:
        #         time.sleep(30)        
        random_sleep(2, 5)

        # Calculate date 3 days from today
        date_str = config.target_date.strftime("%d-%m-%Y")

        # Renaming the file
        realpath = 'C:\DomCop\Expiring'
        download_path = glob.glob("C:\DomCop\Expiring\*") 
        random_sleep(2, 5)  # Allow a short delay for download to complete
        latest_filename = max(download_path, key=os.path.getctime)
        print(f'Latest downloaded file is :{latest_filename}')

        desired_filename = ""  # Initialize empty, will set filename later
        if url == URLS[0]:
            desired_filename = f"Dropped_{date_str}.csv"
        elif url == URLS[1]:
            desired_filename = f"Auction_{date_str}.csv"
        elif url == URLS[2]:
            desired_filename = f"Bad_{date_str}.csv"

        if desired_filename:
            src = os.path.join(realpath, latest_filename)
            dst = os.path.join(realpath, desired_filename)
            try:
                os.rename(src, dst)
            except Exception as e:
                print("create a duplicate name " + str(e))
                desired_filename = desired_filename[:-4] + "_1.csv" 
                dst = os.path.join(realpath, desired_filename)
                os.rename(src, dst)
            
            print("File renamed to:", desired_filename)
        else:
            print('rename failed..')
        
    except Exception as error:
        print(error)
        print('something wrong.. browser quit')
        driver.quit()

if __name__ == "__main__":
   for url in URLS:
       main(driver, url)
       
# FTP server credentials
FTP_HOST = "ams22.stablehost.com"
FTP_PORT = "21"
FTP_USER = "traffic@localproduction.net"
FTP_PASS = "x;B)S%4#_UQ~"

# Local folder path
LOCAL_FOLDER = "C:\DomCop\Expiring"

# Function to get the 3 latest files
def get_latest_files(folder_path, n=3):
    files = [(os.path.join(folder_path, f), os.path.getmtime(os.path.join(folder_path, f))) 
            for f in os.listdir(folder_path)]
    return sorted(files, key=lambda x: x[1], reverse=True)[:n]

# Connect to the FTP server
with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
    print("FTP connection established")
    random_sleep(2, 5)

    # Change to the desired directory on the FTP server (optional)
    ftp.cwd("domcop")  # Replace 'target_directory' if needed

    # Get the latest files
    latest_files = get_latest_files(LOCAL_FOLDER)

    # Upload each file
    for file_path, _ in latest_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as file:
            print(f"Uploading {filename}...")
            ftp.storbinary('STOR ' + filename, file)
            print("Upload complete")

print("All files uploaded successfully")

driver.quit()