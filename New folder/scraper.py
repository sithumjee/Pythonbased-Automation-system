from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_ecommerce_site():
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()  # Ensure the correct path to your ChromeDriver
    driver.get('https://www.amazon.com/s?k=nintendo+i&ref=nb_sb_noss_2')  # URL of the e-commerce site

    extracted_data = []
    
    while True:
        time.sleep(3)  # Wait for the page to load

        items = driver.find_elements(By.CSS_SELECTOR, '.s-main-slot .s-result-item')
        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, 'h2 .a-link-normal').text
                price = item.find_element(By.CSS_SELECTOR, '.a-price .a-offscreen').text
                availability = item.find_element(By.CSS_SELECTOR, '.a-color-success').text if item.find_elements(By.CSS_SELECTOR, '.a-color-success') else "Not available"
                rating = item.find_element(By.CSS_SELECTOR, '.a-icon-alt').text if item.find_elements(By.CSS_SELECTOR, '.a-icon-alt') else "No rating"
                
                extracted_data.append({
                    'name': name,
                    'price': price,
                    'availability': availability,
                    'rating': rating
                })
            except Exception as e:
                print(f"Error extracting data: {e}")

        # Check for the next page button and click it if available
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@class, "s-pagination-next")]'))
            )
            if "a-disabled" in next_button.get_attribute('class'):
                print("Next button is disabled, stopping pagination.")
                break  # No more pages to scrape
            next_button.click()
        except Exception as e:
            print("No more pages or error navigating to the next page:", e)
            break

    driver.quit()
    return extracted_data

def submit_data_to_form(data):
    # Set up the Selenium WebDriver for form submission
    driver = webdriver.Chrome()  # Ensure the correct path to your ChromeDriver
    driver.get('http://localhost:5000/')  # Replace with your form URL

    for product in data:
        driver.find_element(By.ID, 'name').send_keys(product['name'])
        driver.find_element(By.ID, 'price').send_keys(product['price'])
        driver.find_element(By.ID, 'availability').send_keys(product['availability'])
        driver.find_element(By.ID, 'rating').send_keys(product['rating'])
        
        driver.find_element(By.XPATH, '//button[text()="Update"]').click()  # Adjust button text if necessary
        time.sleep(2)  # Wait for the form to be processed

    driver.quit()

if __name__ == "__main__":
    data = scrape_ecommerce_site()
    submit_data_to_form(data)
