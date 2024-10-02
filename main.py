import json
import pickle
import time

import lxml
import requests
from lxml import html
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
from lxml import etree
import datetime
import traceback

from selenium.webdriver.support.wait import WebDriverWait

import asyncio
import nodriver as uc


async def parse_cloudflare():
    browser = await uc.start()
    url = "https://in.bookmyshow.com/events/vidyasagar-the-greatest-hits-live-in-bengaluru/ET00411944"
    url = "https://in.bookmyshow.com/events/namak-ishq-ka/ET00408911"
    # url = "https://in.bookmyshow.com/events/namak-ishq-ka/ET00408911/seat-layout/seatscanvas/MUKH/10305"
    page = await browser.get(url)

    await page.save_screenshot()
    await page.get_content()
    await page.scroll_down(150)
    elems = await page.select_all('*[src]')
    for elem in elems:
        await elem.flash()

    # create_account = await page.find("mumbai", best_match=True)
    # await create_account.click()
    # await await asyncio.sleep((3)
    #
    # create_account = await page.find("improv pilot", best_match=True)
    # await create_account.click()
    # await await asyncio.sleep((3)

    create_account = await page.find("Book", best_match=True)
    await create_account.click()
    await asyncio.sleep(5)

    create_account = await page.find("Mumbai", best_match=True)
    await create_account.click()
    await asyncio.sleep(3)

    # create_account = await page.find_elements_by_text("7", tag_hint="df-ph.df-t")
    create_account = await page.find_all("7")
    element = None
    for x in create_account:
        if "df-bu" in " ".join(x.attributes):
            element = x
    await element.click()
    await asyncio.sleep(5)

    create_account2 = await page.find_all("canvas-wrapper")
    element = create_account2[0]
    start_x = 500
    start_y = 800
    step = 50
    # await element.mouse_drag((start_x, start_y), steps=50)
    for x in range(50, 200, 10):
        for y in range(200, 500, 10):
            print(x, y)
            js_function = f"""
            function clickOnCanvas(canvas) {{
                const clickEvent = new MouseEvent('click', {{
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: canvas.getBoundingClientRect().left + {x},
                    clientY: canvas.getBoundingClientRect().top + {y}
                }});
                consolelog(canvas.getBoundingClientRect().left + {x});
                consolelog(canvas.getBoundingClientRect().left + {y});
                canvas.dispatchEvent(clickEvent);
            }}
            """
            await element.apply(js_function=js_function)
            # await element.mouse_drag((start_x + x * step, start_y + y * step), steps=2)
            # await element.mouse_click()
            await asyncio.sleep(4)

    # create_account1 = await page.find_all("26")

    create_account = await page.find("Add", best_match=True)
    await create_account.click()
    await asyncio.sleep(5)

    create_account = await page.find("Proceed", best_match=True)
    await create_account.click()
    await asyncio.sleep(5)

    create_account = await page.find("Login to proceed", best_match=True)
    await create_account.click()
    await asyncio.sleep(5)

    create_account = await page.find("Continue with email", best_match=True)
    await create_account.click()
    await asyncio.sleep(10)

    await page.save_screenshot()

    name = await page.select("input[type=text]")
    # again, send random text
    print('filling in the "name" input field')
    from tempmail import EMail

    email = EMail()
    print(email.address)
    await name.send_keys(email.address)

    await asyncio.sleep(100)
    # browser.find_element(
    #     By.XPATH,
    #     # "/html/body/div[3]/div/div/div/div[3]/ul/li[1]",
    #     "/html/body/div[9]/div/div/div/div[3]/ul/li[1]/div/div/img",
    # ).click()

    # page2 = await browser.get('https://twitter.com', new_tab=True)
    # page3 = await browser.get('https://github.com/ultrafunkamsterdam/nodriver', new_window=True)
    #
    # for p in (page, page2, page3):
    #     await p.bring_to_front()
    #     await p.scroll_down(200)
    #     await p  # wait for events to be processed
    #     await p.reload()
    #     if p != page3:
    #         await p.close()


usual_wait_time = 10


async def login_with_email(driver):
    await button_click(driver, "//div[@id='modal-root']/div/div/div/div/div[2]/div/div[1]/div/div[2]/div/div",
                       error_msg="Failed to click Continue with email")

    from tempmail import EMail
    email = EMail()
    print(email.address)

    for _ in range(3):
        await asyncio.sleep(usual_wait_time)
        try:
            email_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH,
                "//div[@id='modal-root']/div/div/div/div/div[2]/form/div[1]/div[2]/input"
            )))
            await asyncio.sleep(1)
            email_input.send_keys(email.address)
            email_input.send_keys(Keys.RETURN)
            break
        except Exception as e:
            print(f"Failed to Find email input: {e}")

    # click continue to get otp code
    await button_click(driver, "//div[@id='modal-root']/div/div/div/div/div[2]/form/div[2]/button",
                       error_msg="Failed to send email")

    msg = email.wait_for_message()
    try:
        otp = msg.subject[:6]
        print(f"otp = [{otp}]")
    except Exception as e:
        print(f"Failed access otp code: {e}")

    for _ in range(3):
        try:
            await asyncio.sleep(usual_wait_time)
            digits = driver.find_elements(
                By.XPATH,
                "//div[@id='modal-root']/div/div/div/div/div[2]/form/div[1]/div[3]/input"
            )
            for otp_digit, digit in zip(otp, digits):
                digit.send_keys(otp_digit)
            break
        except Exception as e:
            print(f'failed digits: {e}')


async def button_click(driver, xpath, tries=3, error_msg="", default_timeout=3):
    for _ in range(tries):
        try:
            await asyncio.sleep(usual_wait_time)
            WebDriverWait(driver, default_timeout).until(EC.visibility_of_element_located((
                By.XPATH,
                xpath
            ))).click()
            break
        except Exception as e:
            print(f'{error_msg}: {traceback.format_exc()}')


drivers = {}


async def parse_cloudflate_uc(port=11001):
    import undetected_chromedriver as uc
    seleniumwire_options = {
        "proxy": {
            "http": f"<YOUR_PROXY>:{port}",
            "https": f"<YOUR_PROXY>:{port}"
        },
    }
    driver = uc.Chrome(headless=False, use_subprocess=False, version_main=129,
                       seleniumwire_options=seleniumwire_options
                       )

    instant_login = True
    url = "https://in.bookmyshow.com/events/namak-ishq-ka/ET00408911"
    # url = "https://in.bookmyshow.com/events/ymoys-in-concert/ET00407426"
    driver.get(url)
    driver.maximize_window()
    await button_click(driver, "/html/body/div[3]/div/div/div/div[3]/ul/li[1]/div/div/img", tries=8,
                       error_msg="Failed click Mumbai")

    # sign in
    if instant_login:
        await button_click(driver,
                           "/html/body/div[2]/div/div/div/div/header/div[1]/div/div/div/div[2]/div[2]/div[1]",
                           error_msg="Failed click sign-in")
        await login_with_email(driver)

    await button_click(driver,
                       "/html/body/div[2]/div/div/div/div/div[2]/div/header/div/div/div[1]/div[2]/div/div/button",
                       tries=8,
                       error_msg="Failed click Book")

    await button_click(driver, "/html/body/div[2]/div/div/div[4]/div[4]/div/div[3]/div[1]",
                       error_msg="Failed click 1")

    from a_selenium_click_on_coords import click_on_coordinates

    done = False
    try:
        start_x = 480
        start_y = 150
        step = 50
        for y in range(10, 200, 10):
            if done:
                break
            for x in range(10, 200, 10):
                if done:
                    break
                print(start_x + x, start_y + y)
                click_on_coordinates(driver, x=start_x + x, y=start_y + y, script_timeout=10)
                await asyncio.sleep(1)
                for _ in range(1):
                    try:
                        button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((
                            By.XPATH,
                            "/html/body/div[2]/div/div/div[4]/div[3]/div/div/div/div[2]/button",
                        )))

                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            await asyncio.sleep(1)
                            try:
                                # if button disappears
                                WebDriverWait(driver, 2).until(EC.element_to_be_clickable((
                                    By.XPATH,
                                    "/html/body/div[2]/div/div/div[4]/div[3]/div/div/div/div[2]/button",
                                ))).click()
                            except:
                                done = True
                                break
                    except:
                        print('Not proceed')
    except Exception as e:
        print(f"Failed click: {e}")

    print('WAIT FOR NEXT STEPS')
    # await asyncio.sleep((60)

    await button_click(driver, "/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/div/div/button",
                       error_msg="Failed to click Proceed to login")

    if not instant_login:
        await login_with_email(driver)

    for _ in range(3):
        try:
            await asyncio.sleep(usual_wait_time)
            phone = driver.find_element(
                By.XPATH,
                "/html/body/div[5]/div/div/div[3]/div[1]/div[3]/div[2]/div/div[1]/div[2]/input"
            )
            phone.send_keys("8956629119")
            break
        except Exception as e:
            print(f'failed phone: {e}')

    for _ in range(3):
        try:
            await asyncio.sleep(usual_wait_time)
            email = driver.find_element(
                By.XPATH,
                "/html/body/div[5]/div/div/div[3]/div[1]/div[3]/div[2]/div/div[1]/div[1]/input"
            )
            email.clear()
            email.send_keys("mg@manish.cc")
            break
        except Exception as e:
            print(f'failed email: {e}')

    await button_click(driver, "/html/body/div[5]/div/div/div[3]/div[1]/div[3]/div[2]/div/div[1]/div[3]/a",
                       error_msg="Failed to approve contacts")

    await button_click(driver, "/html/body/div[5]/div/div/div[3]/div[1]/div[9]/div[2]/div/div[2]/ul/li[6]",
                       error_msg="Failed to click gift voucher")

    for _ in range(3):
        try:
            await asyncio.sleep(usual_wait_time)
            voucher = driver.find_element(
                By.XPATH,
                "/html/body/div[5]/div/div/div[3]/div[1]/div[9]/div[2]/div/div[3]/div[16]/div[1]/input"
            )
            voucher.send_keys("8S2CFWPPWL")
            break
        except Exception as e:
            print(f'failed voucher: {e}')

    await button_click(driver, "/html/body/div[5]/div/div/div[3]/div[1]/div[9]/div[2]/div/div[3]/div[16]/div[1]/button",
                       error_msg="Failed to click gift voucher button apply")

    await button_click(driver, "/html/body/div[5]/div/div/div[3]/div[2]/div[1]/div[2]/button",
                       error_msg="Failed to click confirm")

    print("TO CLICK OTP")
    await asyncio.sleep(200)
    # "/html/body/div[13]/div/div/div/div/div[2]/form/div[1]/div[3]/input[2]"

    return "Done"


# since asyncio.run never worked (for me)

def save_driver_info(driver, port):
    with open(f"session_{port}.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)


def get_driver(port, use_cookies=False):
    import undetected_chromedriver as uc
    seleniumwire_options = {
        "proxy": {
            "http": f"<YOUR_PROXY>:{port}",
            "https": f"<YOUR_PROXY>:{port}"
        },
    }
    driver = uc.Chrome(headless=False, use_subprocess=False, version_main=129,
                       seleniumwire_options=seleniumwire_options
                       )

    open_coldplay = True
    if open_coldplay:
        url = "https://in.bookmyshow.com/events/coldplay-music-of-the-spheres-world-tour/ET00412466"
        driver.get(url)
        driver.maximize_window()
    if use_cookies:
        load_session(driver, port)
    return driver


def load_session(driver, port):
    with open(f"session_{port}.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()  # Refresh to apply cookies


async def click_book_button_for_coming_soon(port):
    instant_login = True
    already_loggined = True
    url = "https://in.bookmyshow.com/events/coldplay-music-of-the-spheres-world-tour/ET00412466"
    # url = "https://in.bookmyshow.com/events/ymoys-in-concert/ET00407426"
    drivers[port] = get_driver(port, use_cookies=True)
    if not already_loggined:
        drivers[port].get(url)
        drivers[port].maximize_window()
        await button_click(drivers[port], "/html/body/div[3]/div/div/div/div[3]/ul/li[1]/div/div/img", tries=8,
                           error_msg="Failed click Mumbai")

        if instant_login:
            await button_click(drivers[port],
                               "/html/body/div[2]/div/div/div/div/header/div[1]/div/div/div/div[2]/div[2]/div[1]",
                               error_msg="Failed click sign-in")
            await login_with_email(drivers[port])

    uc = True
    if uc:
        # Define the button selector (update as needed)
        button_selector = (
            By.XPATH, "/html/body/div[2]/div/div/div/div/div[2]/div/header/div/div/div[1]/div[2]/div/div/button")

        # Function to detect if the button is active and clickable
        def is_button_clickable(driver):
            try:
                # Wait for the button to be clickable
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable(button_selector)
                )
                return True
            except:
                return False

        # Function to get button text
        def get_button_text(driver):
            try:
                button = driver.find_element(*button_selector)
                return button.text
            except:
                return ""

        # Function to reload the page
        def reload_page(driver):
            driver.refresh()
            print("Page reloaded.")

        # Main logic to detect and click the button, with page reloads

        button_disappears = False
        try:
            while True:
                max_reloads = 10  # Maximum number of reloads to attempt
                reload_count = 0
                while reload_count < max_reloads:
                    button = drivers[port].find_element(*button_selector)
                    button.click()
                    reload_count += 1
                    reload_page(drivers[port])
                    time.sleep(2)  # Adjust the sleep duration as necessary

            # Further logic after the button is clicked
            print("Button clicked successfully. Proceeding with next steps...")
            # Add your next steps here
        except Exception as e:
            button_disappears = True
            print(f"An error occurred: {e}")

        input("Press Enter to exit and close the browser...")
    else:
        drivers[port] = await uc.start()
        url = "https://in.bookmyshow.com/events/coldplay-music-of-the-spheres-world-tour/ET00412466"
        page = await drivers[port].get(url)

        while True:
            create_account = await page.find("Book")
            await asyncio.sleep(2)
            await create_account.click()
            await asyncio.sleep(2)


async def main():
    tasks = []
    for port in range(11001, 11003):
        # drivers[port] = get_driver(port)
        # task = parse_cloudflate_uc(port)
        task = click_book_button_for_coming_soon(port)
        tasks.append((port, task))
    input("Log in and navigate to the desired page, then press Enter to continue...")
    # for port in range(11001, 11003):
    #     save_driver_info(drivers[port], port)
    drivers.clear()
    results = await asyncio.gather(*[t[1] for t in tasks])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(parse_cloudflare())
    loop.run_forever()
    loop.close()

    # parse_cloudflate_uc()
    # asyncio.create_task(main)
    # uc.loop().run_until_complete(main)
    # parse_site()
