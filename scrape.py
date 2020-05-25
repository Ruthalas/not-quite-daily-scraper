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
imageNameType = configparser.get('General', 'imageNameType')
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

# Start looping per page here?

# fetch webpage
currentPageURL = "https://www.truefork.org/Art/comic/cindex.php?44"
driver.get(currentPageURL)

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

# Get the file extension from the URL
URLpath = urlparse(imageLocation).path
ext = os.path.splitext(URLpath)[1]

# Get the original image name from the URL
urlParts = os.path.splitext(URLpath)[0].split("/")
originalImageName = urlParts[len(urlParts)-1] # (It's the last part when split on '/')

# Name the output image file based on the imageNameType toggle
if imageNameType == "title":
    # Set image save name to be the comic title
    imgSaveName = imageTitleText
elif imageNameType == "originalFilename":
    # Set image save name to original image name (based on URL)
    imgSaveName = originalImageName

# Build the final file path for the image using the output dir, the image name, and the image extension
imgSavePathFull = os.path.join(outputPath, imgSaveName + ext)
# Build a similar file path for the text content
txtSavePathFull = os.path.join(outputPath, imgSaveName + ".txt")

print("Comic Title:   " + imageTitleText + "\nComic Comment: " + comicCommentHTML)
print("Saving:  " + imageLocation + "\nTo path: " + imgSavePathFull)

# Write out the image file with the imgSavePathFull we built and the imageLocationn we found
with open(imgSavePathFull, 'wb') as workingFile:
    response = requests.get(imageLocation, stream=True)
    if not response.ok:
        print ("Error saving image: " + response)
    for block in response.iter_content(1024):
        if not block:
            break
        workingFile.write(block)
    workingFile.close()

# Write out a txt file with the comic title and author comment (and source URL)
with open(txtSavePathFull, 'w') as workingFile:
    textStr = imageTitleText + "\n" + comicCommentHTML + "\nSource: " + currentPageURL
    workingFile.write().close()

# Close browser
driver.close()














