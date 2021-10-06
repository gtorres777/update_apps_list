from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import NamedTuple
import argparse
import time
import csv
import requests
import json


class Args(NamedTuple):
    """Command-line arguments"""

    url: str


def get_args() -> Args:

    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Script for Update list of Apps",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("url", metavar="url", help="url of the service")

    args = parser.parse_args()

    return Args(args.url)


def get_list_db(url):
    action_url = "http://{}/web/database/list".format(url)
    data = {"params": {}}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(action_url, data=json.dumps(data), headers=headers)
        db = response.json()
    except Exception as e:
        print("URL:", url)
        print("Connection establishment failed!")
        print(e)
        print("------------------------------")
        db = {"error": e}

    return db


def main() -> None:

    args = get_args()
    url = args.url

    list_of_existing_databases = get_list_db(f"{url}").get("result")

    with open("credentials.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            data = {
                "db_name": row[0],
                "email": row[1],
                "password": row[2],
            }

            if data["db_name"] in list_of_existing_databases:

                try:

                    print("Running actions for database:",data['db_name'])

                    ### Instantiating chrome driver for selenium ###
                    chrome_options = Options()
                    chrome_options.add_argument("--kiosk")
                    driver = webdriver.Chrome(options=chrome_options)

                    ### Connecting to the url given
                    driver.get("http://" + url)

                    ### selecting the database from the list
                    select_db = driver.find_element_by_xpath(
                        "//a[@href='/web?db={}']".format(data["db_name"])
                    )
                    select_db.click()
                    driver.implicitly_wait(3)

                    ### Setting the credentials to acces the database selected
                    value_for_input_email = data["email"]
                    value_for_input_password = data["password"]

                    input_email = driver.find_element_by_xpath("//input[@name='login']")
                    input_password = driver.find_element_by_xpath(
                        "//input[@name='password']"
                    )

                    input_email.send_keys(value_for_input_email)
                    input_password.send_keys(value_for_input_password)

                    ### simulating the login access
                    login_button = driver.find_element_by_xpath("//button[@type='submit']")
                    login_button.click()

                    driver.implicitly_wait(3)

                    ###entering to the apps page
                    dropdown_button = driver.find_element_by_xpath(
                        "//li/a/i[@class='fa fa-th-large']"
                    )
                    dropdown_button.click()
                    driver.implicitly_wait(3)

                    apps_dropdown_button = driver.find_element_by_xpath(
                        "//li/div/a[@data-menu-id='5']"
                    )
                    apps_dropdown_button.click()
                    driver.implicitly_wait(3)

                    ### Obtaining the url to modify it to access to debug mode
                    current_url = driver.current_url

                    separated_url = current_url.split("web")

                    updated_url_for_developer_mode = (
                        separated_url[0] + "web?debug=1" + separated_url[1]
                    )

                    driver.get(updated_url_for_developer_mode)

                    driver.implicitly_wait(3)

                    ### Clicking the "Update Apps list" button
                    update_button = driver.find_element_by_xpath("//li/a[@data-menu='55']")
                    update_button.click()
                    driver.implicitly_wait(3)

                    ### Clicking the confirm update button in the modal that appears
                    update_confirm_button = driver.find_element_by_xpath(
                        "//button[@name='update_module']"
                    )
                    update_confirm_button.click()
                    driver.implicitly_wait(3)

                    ### Time in seconds to wait before passing to the other database
                    time.sleep(60)

                    ### Closing the instance
                    driver.quit()

                    print("Success")
                    print("------------------------------\n")

                except Exception as e:
                    print("Fail")
                    print("URL:", url)
                    print("Database:", data['db_name'])
                    print(e)
                    print("------------------------------\n")


# --------------------------------------------------
if __name__ == "__main__":
    main()
