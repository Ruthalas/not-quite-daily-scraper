# Import modules we will be using
import configparser
import requests
import os
from urllib.parse import urlparse
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

# Start looping per page here?

# Grab content elements based on the paths provided
comicComment = driver.find_elements_by_xpath(commentPath)
comicImage = driver.find_elements_by_xpath(imagePath)
imageTitle = driver.find_elements_by_xpath(imageTitlePath)
nextButton = driver.find_elements_by_xpath(nextButtonPath)

# Extract content out of those elements
comicCommentHTML = comicComment[0].get_attribute('innerHTML')
imageLocation = comicImage[0].get_attribute('src')
imageTitleText = imageTitle[0].text
nextButtonLocation = nextButton[0].get_attribute('href')

imgSavePath = 'pic1'
path = urlparse(imageLocation).path
ext = os.path.splitext(path)[1]
imgSavePathFull = imgSavePath + ext

print("Comic Title:   " + imageTitleText + "\nComic Comment: " + comicCommentHTML)
print("Saving:  " + imageLocation + "\nTo path: " + imgSavePathFull)

with open(imgSavePathFull, 'wb') as handle:
        response = requests.get(imageLocation, stream=True)
        if not response.ok:
            print (response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

# Close browser
driver.close()
