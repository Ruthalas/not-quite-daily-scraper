# Import modules we will be using
import configparser
import requests
from selenium import webdriver

# Pull in variables from config file
configparser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configparser.read(configFilePath)
# General group
outputPath = configparser.get('General', 'outputPath')
subfolderToggle = configparser.get('General', 'subfolderToggle')
getComments = configparser.get('General', 'getComments')
# Comic group
comicName = configparser.get('Comic', 'comicName')
commentPath = configparser.get('Comic', 'commentPath')
imageTitlePath = configparser.get('Comic', 'imageTitlePath')
nextButtonPath = configparser.get('Comic', 'nextButtonPath')
imagePath = configparser.get('Comic', 'imagePath')

# Set up the browser we'll be using
driverOptions = webdriver.FirefoxOptions()
driverOptions.headless = True
driver = webdriver.Firefox(options=driverOptions)
# fetch webpage
driver.get("https://www.truefork.org/Art/comic/cindex.php?44")

# Grab content based on the paths provided
comicComment = driver.find_elements_by_xpath(commentPath)
comicImage = driver.find_elements_by_xpath(imagePath)
imageTitle = driver.find_elements_by_xpath(imageTitlePath)
nextButton = driver.find_elements_by_xpath(nextButtonPath)

print(imageTitle[0].text + "\n" + comicComment[0].get_attribute('innerHTML'))

imageLocation = comicImage[0].get_attribute('src')

with open('pic1.jpg', 'wb') as handle:
        response = requests.get(imageLocation, stream=True)
        if not response.ok:
            print (response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

# Close browser
driver.close()
