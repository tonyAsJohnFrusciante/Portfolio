from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import re

START = time.time()

driver = webdriver.Chrome()

url = "https://toscrape.com/"
driver.get(url)

driver.maximize_window()
time.sleep(2)

image = driver.find_element(By.XPATH, "//img[@src='./img/books.png']")
image.click()
time.sleep(2)

books = {}

while True:
    pods = driver.find_elements(By.CLASS_NAME, "product_pod")
    for pod in pods:
        # Get Rating
        rating_class = pod.find_element(By.CSS_SELECTOR, "p.star-rating")
        class_attribute = rating_class.get_attribute("class")
        rating = class_attribute.split()[-1]

        # Get Price
        price_class = pod.find_element(By.CLASS_NAME, "price_color")
        price = price_class.text

        # Get Title and Rating
        a_element = pod.find_element(By.CSS_SELECTOR, "h3 a")

        href = a_element.get_attribute("href")
        title = a_element.get_attribute("title")

        books[title] = [rating, price, href]

    try:
        next_button_element = driver.find_element(By.CLASS_NAME, 'next')
        click_button = next_button_element.find_element(By.TAG_NAME, "a")
        click_button.click()
        time.sleep(2)
    except:
        break

print(time.time() - START)

# Save information as CSV after we small preprocessing
df = pd.DataFrame(list(books.items()), columns=["Title", "Information"])
df["Rating"] = [x[0] for x in df["Information"]]
df["Price"] = [float(x[1].replace("£", "")) for x in df["Information"]]
df["Url"] = [x[2] for x in df["Information"]]
df = df.drop(["Information"], axis=1)
df.to_csv("bookstore.csv", index=False)

# Change the rating to numbers
char_to_num = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["Rating"] = df["Rating"].map(char_to_num)

# Task A - find mean Price and Rating
mean_price = df["Price"].mean()
print(f"The mean price of a book in our store is {round(mean_price)}£.")

mean_rating = df["Rating"].mean()
print(f"The average rating of a book in our store is {round(mean_rating, 1)}.")

# Task B - visualize the number of books for each rating category
rating_counts = df['Rating'].value_counts().sort_index()

fig, ax = plt.subplots()
bars = ax.bar(rating_counts.index, rating_counts.values, color='skyblue')

plt.title('Number of Books in Each Rating Category')
plt.xlabel('Rating')
plt.ylabel('Number of Books')
plt.xticks(rotation=45)

plt.ylim(100, max(rating_counts.values) + 10)

for bar, count in zip(bars, rating_counts.values):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, yval + 1, str(count), ha='center', va='bottom', color='black',
            fontweight='bold')

plt.show()

# Task C & D - Get the stock availability and the description for each book of the top 3 and the bottom 3 in price.

# Isolate the 6 books of interest in 2 dataframes
top3_price = df.nlargest(3, 'Price')['Url']
bottom3_price = df.nsmallest(3, 'Price')['Url']

top3_dict, bot3_dict = {}, {}


def get_inner_info(driver):
    stock_element = driver.find_element(By.CLASS_NAME, "instock.availability")
    stock_text = stock_element.text
    parentheses_content = re.search(r'\((.*?)\)', stock_text).group(1)
    stock = parentheses_content.split()[0]
    title = df.loc[df["Url"] == item, "Title"].values[0]

    description_element = driver.find_element(By.CLASS_NAME, "product_page")
    description = description_element.find_element(By.XPATH, "./p").text

    return title, stock, description


for item in top3_price:
    driver.get(item)
    time.sleep(2)
    title, stock, description = get_inner_info(driver)
    top3_dict[title] = [stock, description]

for item in bottom3_price:
    driver.get(item)
    time.sleep(2)
    title, stock, description = get_inner_info(driver)
    bot3_dict[title] = [stock, description]

driver.quit()

print(top3_dict)
print(bot3_dict)