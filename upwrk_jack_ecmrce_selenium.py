# Import necessary modules
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()

# URL to scrape
url = "https://use_your_url.com"
driver.get(url)
print(f"Opened URL: {url}")
time.sleep(random.uniform(2, 5))

# Initialize an empty list to store scraped data
all_data = []

# Start scraping the products on the page
try:
    # Locate product links on the page
    print("Finding product links...")
    product_elements = driver.find_elements(By.XPATH, "//h3[@class='card__heading']//a[contains(@class, 'full-unstyled-link')]")
    product_links = [element.get_attribute("href") for element in product_elements if element.get_attribute("href")]
    print(f"Found {len(product_links)} product links.")
    testing = 0
    # itterate through each product link and open the current window
    for product_url in product_links:
        print(f"Processing product: {product_url}")
        driver.execute_script("window.open(arguments[0], '_blank');", product_url)
        time.sleep(random.uniform(1, 3))
        new_tab = driver.window_handles[-1]
        driver.switch_to.window(new_tab)
        # comment this block if you want run for the whole site
        testing +=1
        if testing >=4:
            break

        # title extarction
        try:
            title_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='product__title']//h1"))
            )
            title = title_element.text.strip()
            print(f"Title: {title}")
        except TimeoutException:
            title = "Title not found"
            print("Title not found!")

        # colors extarction
        count_variable = 0
        while True:
            color_xpath = f"//input[contains(@id, 'main-1-{count_variable}')]"
            try:
                color_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, color_xpath))
                )
                
                # do not extract the product which not in stock
                if "disabled" not in color_element.get_attribute("class"):
                                        
                    color = color_element.get_attribute("value")
                    print(f"Processing color: {color}")
                    time.sleep(random.uniform(2, 3))
                    driver.execute_script("arguments[0].click();", color_element)
                    time.sleep(random.uniform(1, 3))
                else:
                    stock_out_color = color_element.get_attribute("value")
                    print(f"{stock_out_color} This color product is OUT of stock")
               
                #color = color_element.get_attribute("value")
                #print(f"Processing color: {color}")
                #time.sleep(random.uniform(2, 3))
                #driver.execute_script("arguments[0].click();", color_element)
                #time.sleep(random.uniform(1, 3))

                # price extraction
                try:
                    price_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='price__regular']//span[2]"))
                    )
                    
                    price = price_element.text.strip()
                    # Remove the dollar sign and "USD", then convert to a float  
                    price_value = float(price.replace('$', '').replace(' USD', '').strip())
                    time.sleep(random.uniform(2, 5))
                    print(f"Price: {price}")
                    print(f"Price_Value:{price_value}")
                except TimeoutException:
                    price = "Price not found"
                    print("Price not found!")

                # sizes
                sizes = [] # empty list for sizes. later we extract and append
                try:
                    size_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//input[contains(@id, 'main-2-')]")) # explicit wait
                    )
                    
                    for size_element in size_elements:
                        if "disabled" not in size_element.get_attribute("class"):
                            sizes.append(size_element.get_attribute("value"))
                    print(f"Sizes: {sizes}")
                except TimeoutException:
                    sizes = []
                    print("Sizes not found!")

                # Store product details
                for size in sizes:
                    product_data = {
                        'Title': f'{title}, {color}, size: {size}',
                        'Price': price_value,
                        'Color': color,
                        'Size': size,
                        'URL': product_url
                    }
                    all_data.append(product_data)
                    print(f"Added data: {product_data}")

                # Increment color counter inorder loop through the xpath of current page
                count_variable += 1
            except TimeoutException:
                print("No more colors to process for this product.")
                break

        # Close the product tab and switch back to the main page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(random.uniform(2, 3))
        print("Closed product tab and switched back.")

    # Save data to CSV
    if all_data:
        print("Saving data to CSV...")
        df = pd.DataFrame(all_data)
        df.to_csv("testing_scraped_products.csv", index=False)
        print("Data saved successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
