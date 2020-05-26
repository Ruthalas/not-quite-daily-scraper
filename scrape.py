# Import modules we will be using
import configparser
import requests
import os
import sys
from urllib.parse import urlparse
from selenium import webdriver

# Replace various characters that would be illegal in a filename (Windows)
def sanitizeString(stringToClean):
    naughtyCharList = ['/','>','<',':','"','|','?','*','\\']
    replacementChar = "-"
    # Iterate through each naughty option and replace any instances of it in stringToClean
    for elem in naughtyCharList :
        # Check if string is in the main string
        if elem in stringToClean :
            # Replace the string
            stringToClean = stringToClean.replace(elem, replacementChar)
    return stringToClean


if not os.path.isfile(sys.argv[1]):
    print("Please provide a valid file for the config.\nYour provided: " + str(sys.argv[1]))
    raise SystemExit(0)
else:
    print("Config file found.")
    configFilePath = sys.argv[1]

# Pull in variables from config file
configparser = configparser.RawConfigParser()
configparser.read(configFilePath)
# General group
outputPath = configparser.get('General', 'outputPath')
subfolderToggle = configparser.get('General', 'subfolderToggle')
getComments = configparser.get('General', 'getComments')
getImage = configparser.get('General', 'getImage')
imageNameType = configparser.get('General', 'imageNameType')
# Comic group
comicName = configparser.get('Comic', 'comicName')
comicStartPage = configparser.get('Comic', 'comicStartPage')
commentPath = configparser.get('Comic', 'commentPath')
imageTitlePath = configparser.get('Comic', 'imageTitlePath')
nextButtonPath = configparser.get('Comic', 'nextButtonPath')
imagePath = configparser.get('Comic', 'imagePath')

print("Config settings imported.")

# If the user requested a subfolder, append it to the current outputPath
if subfolderToggle == "True":
    outputPath = os.path.join(outputPath, comicName)

# Check if the desired output directory exists, if not, create it
if not os.path.isdir(outputPath):
    print("Output directory does not yet exist, creating.")
    os.mkdir(outputPath)
else:
    print("Output directory found.")

# Set up the browser we'll be using
driverOptions = webdriver.FirefoxOptions()
driverOptions.set_preference("general.useragent.override", "Not Quite Daily Scraper")
driverOptions.headless = True
driver = webdriver.Firefox(options=driverOptions)

print("Browser created. Beginning to scrape " + comicName)

# Start with current page, and begin grabbing contents
# (Each loop will reset currentPageURL to the next page, via the contents of the next button)
currentPageURL = comicStartPage

lastPage = False
while lastPage == False:

    # First try the webpage and makes sure it returns a good error code
    request = requests.get(currentPageURL)
    if request.status_code == 200:
        # Nice! The page exists and returns a good code
        print('\nAccessing page: ' + currentPageURL)
    else:
        # If we can't find the current page, let the user know and break out of the while loop
        print('\nPage unavailable: ' + currentPageURL)      
        break
    
    # If we found the page, let's open it in Gecko to start our parsing
    driver.get(currentPageURL)

    # Grab content elements based on the paths provided (skip ones the user has turned off)
    if getComments == "True":
        comicComment = driver.find_elements_by_xpath(commentPath)
    if getImage == "True":
        comicImage = driver.find_elements_by_xpath(imagePath)
    imageTitle = driver.find_elements_by_xpath(imageTitlePath)
    nextButton = driver.find_elements_by_xpath(nextButtonPath)

    # Check to see if a next button exists, if not, break
    if len(nextButton) < 1:
        print("\nNo next page button found on this page.\nWe've likely hit the current page!")
        break

    # Extract content out of those elements (skip ones the user has turned off)
    if getComments == "True":
        comicCommentHTML = comicComment[0].get_attribute('innerHTML')
    if getImage == "True":
        imageLocation = comicImage[0].get_attribute('src')
    imageTitleText = imageTitle[0].text
    nextButtonLocation = nextButton[0].get_attribute('href')

    # Lets quickly remove any characters from that title that may cause issues later
    imageTitleText = sanitizeString(imageTitleText)

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
    txtSavePathFull = os.path.join(outputPath, imgSaveName + ".html")

    print("  Comic Title: " + imageTitleText)
    print("  Saving: " + imageLocation + "\n  To path: " + imgSavePathFull)

    # If the user requested we get the comic image
    if getImage == "True":
        # If the image file we are about to write doesn't already exist...
        if not os.path.isfile(imgSavePathFull):
            # Write out the image file with the imgSavePathFull we built and the imageLocationn we found
            with open(imgSavePathFull, 'wb') as workingFile:
                response = requests.get(imageLocation, stream=True)
                if not response.ok:
                    print ("  Error saving image: " + response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    workingFile.write(block)
                workingFile.close()
                print("  Image saved.")
        else:
            print("  Image skipped. Found existing.")
    
    # If the user has requested we get an author comment
    if getComments == "True":
        # If the text file we are about to write doesn't already exist...
        if not os.path.isfile(txtSavePathFull):
            # Write out a txt file with the comic title and author comment (and source URL) to the txtSavePathFull we built
            with open(txtSavePathFull, 'w', encoding="utf-8") as workingFile:
                textStr = "<center><p><a href=\"" + currentPageURL + "\">" + imageTitleText + "</a></p></center>" + comicCommentHTML 
                workingFile.write(textStr)
                workingFile.close()
                print("  Comment saved.")
        else:
            print("  Comment skipped. Found existing.")

    # Now that we are done getting all the content for this page,
    # set the currentPageURL to be the next page! 
    currentPageURL = nextButtonLocation

# Close browser
driver.close()

print("\nAll available pages scraped. Exiting.")










