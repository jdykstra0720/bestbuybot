import bs4
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# ---------------------------------------------Please Read--------------------------------------------------------------

# Updated: 9/21/2021

# Let's go over the checklist for the script to run properly.
#   1. Product URL
#   2. Firefox Profile
#   3. Credit Card CVV Number

# This Script only accepts Product URL's that look like this. I hope you see the difference between page examples.


# -----------------------------------------------Steps To Complete------------------------------------------------------

test_mode = False  # Set test_mode to True when testing bot checkout process, and set it to False when your done testing.
headless_mode = False  # Set False for testing. If True, it will hide Firefox in background for faster checkout speed.
webpage_refresh_timer = 3  # Default 3 seconds. If slow internet and the page isn't fully loading, increase this.

# 1. Product URL
url = 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3060-ti-8gb-gddr6-pci-express-4-0-graphics-card-steel-and-black/6439402.p?skuId=6439402'


# 2. Firefox Profile
def create_driver():
    """Creating firefox driver to control webpage. Please add your firefox profile down below."""
    options = Options()
    options.headless = headless_mode
    profile = webdriver.FirefoxProfile(r'C:\Users\Jarod\AppData\Roaming\Mozilla\Firefox\Profiles\z51j1y8y.default-release')
    web_driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return web_driver


# 3. credit card CVV Number
CVV = '123'  # You can enter your CVV number here in quotes.



# ----------------------------------------------------------------------------------------------------------------------


def time_sleep(x, driver):
    """Sleep timer for page refresh."""
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('Monitoring Page. Refreshing in{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.execute_script('window.localStorage.clear();')
    driver.refresh()


def extract_page():
    """bs4 page parser."""
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def driver_click(driver, find_type, selector):
    """Driver Wait and Click Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'xpath':
            try:
                driver.find_element_by_xpath(f"//*[@class='{selector}']").click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)


def searching_for_product(driver):
    """Scanning for product."""
    driver.get(url)

    print("\nWelcome To Bestbuy Bot!")
    print("Bot deployed!\n")

    while True:
        soup = extract_page()
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 5)

        try:
            add_to_cart_button = soup.find('button', {
                'class': 'btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button'})

            if add_to_cart_button:
                print(f'Add To Cart Button Found!')

                # Queue System Logic.
                try:
                    # Entering Queue: Clicking "add to cart" 2nd time to enter queue.
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                    driver_click(driver, 'css', '.add-to-cart-button')
                    print("Clicked Add to Cart Button. Now sending message to your phone.")
                    print("You are now added to Best Buy's Queue System. Page will be refreshing. Please be patient. It could take a few minutes.\n")

                    # Sleep timer is here to give Please Wait Button to appear. Please don't edit this.
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(5)
                except (NoSuchElementException, TimeoutException) as error:
                    print(f'Queue System Error: ${error}')


                # In queue, just waiting for "add to cart" button to turn clickable again.
                # page refresh every 15 seconds until Add to Cart button reappears.
                # When bot clicks "Add to Cart" button, a request is sent to server, and server is just waiting for a response.
                # No possible way to lose your spot once request is sent.
                while True:
                    try:
                        add_to_cart = driver.find_element_by_css_selector(".add-to-cart-button")
                        please_wait_enabled = add_to_cart.get_attribute('aria-describedby')

                        if please_wait_enabled:
                            driver.refresh()
                            time.sleep(15)
                        else:  # When Add to Cart appears. This will click button.
                            print("Add To Cart Button Clicked A Second Time.\n")
                            wait2.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button")))
                            time.sleep(2)
                            driver_click(driver, 'css', '.add-to-cart-button')
                            time.sleep(2)
                            break
                    except(NoSuchElementException, TimeoutException) as error:
                        print(f'Queue System Refresh Error: ${error}')

                # Going To Cart Process.
                driver.get('https://www.bestbuy.com/cart')

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    time.sleep(1)
                    driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary')
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    time_sleep(3, driver)
                    searching_for_product(driver)

                # Logging Into Account.
                print("\nAttempting to Login. Firefox should remember your login info to auto login.")
                print("If you're having trouble with auto login. Close all firefox windows.")
                print("Open firefox manually, and go to bestbuy's website. While Sign in, make sure to click 'Keep Me Logged In' button.")
                print("Then run bot again.\n")

                # Click Shipping Option. (if available)
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    time.sleep(2)
                    shipping_class = driver.find_element_by_xpath("//*[@class='ispu-card__switch']")
                    shipping_class.click()
                    print("Clicking Shipping Option.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as error:
                    print(f'shipping error: {error}')

                # Trying CVV
                try:
                    print("\nTrying CVV Number.\n")
                    wait2.until(EC.presence_of_element_located((By.ID, "credit-card-cvv")))
                    time.sleep(1)
                    security_code = driver.find_element_by_id("credit-card-cvv")
                    time.sleep(1)
                    security_code.send_keys(CVV)
                except (NoSuchElementException, TimeoutException):
                    pass

                # Final Checkout.
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    # comment the one down below. vv
                    if not test_mode:
                        print("Product Checkout Completed.")
                        driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary button__fast-track')
                    if test_mode:
                        print("Test Mode - Product Checkout Completed.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Complete Checkout.")

                # Completed Checkout.
                print('Order Placed!')
                time.sleep(1800)
                driver.quit()

        except (NoSuchElementException, TimeoutException) as error:
            print(f'error is: {error}')

        time_sleep(webpage_refresh_timer, driver)


if __name__ == '__main__':
    driver = create_driver()
    searching_for_product(driver)