# Import modules we will be using
import configparser
import requests
import os
import sys
import time
import urllib.request
from urllib.parse import urlparse
from selenium import webdriver

# Check the status response of provided link
# Return 'Good' if 200 or 406, return Null/None if provided empty string, otherwise return the error code
def validLinkCheck(link):
    # Reset values to None/Null
    status = None
    requestResult = None
    # If they didn't send us an empty string, let's check it out
    if (link != ""):
        # Try requesting the webpage and see what it returns
        try:
            request = requests.get(link)
            requestResult = request.status_code
        except Exception as errorCode:
            requestResult = errorCode
    # Return 'Good' or an error code based on whether the status code was good or bad
    # Note: In the case of 406 errors, while something about the page is reported as 'not acceptable', the page will be served, and can therefore be scraped (sometimes...? :/)
    if (requestResult == 200) or (requestResult == 406):
        # Nice! The page exists and returns a good code; return 'Good'
        status = "Good"
    else:
        # Trying to access the URL failed for one reason or another; return that reason
        status = str(requestResult)
    return status

# Replace various characters that would be illegal in a filename (Windows)
def sanitizeString(stringToClean):
    naughtyCharList = ['/','>','<',':','"','|','?','*','\\','#','–']
    replacementChar = "-"
    # Iterate through each naughty option and replace any instances of it in stringToClean
    for elem in naughtyCharList :
        # Check if string is in the main string
        if elem in stringToClean :
            # Replace the portion of the string that matches the neughty list
            stringToClean = stringToClean.replace(elem, replacementChar)
    return stringToClean

# Check if the config file exists (If not, exit script)
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
runHeadless = configparser.get('General', 'runHeadless')
buildHTML = configparser.get('General', 'buildHTML')
# Comic group
comicName = configparser.get('Comic', 'comicName')
comicStartPage = configparser.get('Comic', 'comicStartPage')
commentPath = configparser.get('Comic', 'commentPath')
imageTitlePath = configparser.get('Comic', 'imageTitlePath')
nextButtonPath = configparser.get('Comic', 'nextButtonPath')
nextButtonType = configparser.get('Comic', 'nextButtonType')
imagePath = configparser.get('Comic', 'imagePath')
initialClick = configparser.get('Comic', 'initialClick')

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
if runHeadless == "True":
    driverOptions.headless = True
elif runHeadless == "False":
    driverOptions.headless = False
driver = webdriver.Firefox(options=driverOptions)

print("Browser created. Beginning to scrape " + comicName)

# Prep the loop variables
comicCommentHTML = ""
endLoop = False

# Attempt to load the comicStartPage page, if successful begin loop, if not skip loop (exiting the script)
pageStatus = validLinkCheck(comicStartPage)
if (pageStatus == "Good"):
    # Nice! The page exists and returns a good code
    print('\nAccessing start page: ' + comicStartPage)
else:
    # If we can't find the current page, let the user know and break out of the while loop
    print('\nStart page unavailable: ' + comicStartPage + "\nRequest yielded: " + pageStatus)
    endLoop = True
# If we found the page, let's open it in Gecko to start our parsing
driver.get(comicStartPage)

# If the user requested we perform an initial click, do so!
if (initialClick != ""):
    initialClickContent = driver.find_elements_by_xpath(initialClick)
    initialURL = initialClickContent[0].get_attribute('href')
    print('Clicking initial-click: ' + initialURL)
    driver.get(initialURL)

# Clear the variables we'll be setting each loop to check for repeated errors, and build the 'next page' link 
secondMostRecentURL = ""
mostRecentURL = ""
mostRecentImageURL = ""
txtSavePathName = ""
previousTxtSavePath = ""
overwriteCount = 0
consecutiveSkipCount = 0

while endLoop == False:
    # Record the URL of the current page, regardless of navigation method
    currentPageURL = driver.current_url

    # Grab content elements based on the paths provided (skip ones the user has turned off)
    if getComments == "True":
        comicComment = driver.find_elements_by_xpath(commentPath)
    if getImage == "True":
        comicImage = driver.find_elements_by_xpath(imagePath)
    if imageTitlePath != "":
        imageTitle = driver.find_elements_by_xpath(imageTitlePath)
    else:
        imageTitle = ""

    # Extract comment html, the image url, and the next button url out of those elements (skipping ones the user has turned off)
    # Also save a copy of what the comment was last time, so we don't write out duplicates
    previousCommentHTML = comicCommentHTML
    if getComments == "True":
        # If there isn't anything in the comment element, just leave it blank
        if len(comicComment) < 1:
            comicCommentHTML = ""
        else:
            comicCommentHTML = comicComment[0].get_attribute('innerHTML')
    if getImage == "True":
        # Try to get the comic image URL
        try:
            imageLocation = comicImage[0].get_attribute('src')
            
            # This is to address an issue in SmackJeeves comics (they append stuff to the image URL)
            imageLocation = imageLocation.replace("/dims/optimize","")

            # Get the file extension from the URL
            URLpath = urlparse(imageLocation).path
            ext = os.path.splitext(URLpath)[1]

            # Get the original image name from the URL
            urlParts = os.path.splitext(URLpath)[0].split("/")
            originalImageName = urlParts[len(urlParts)-1] # (It's the last part when split on '/')
        except:
            # If we simply can't find the image, set the image-related variables to default values
            print("  No image found on this page!")
            imageLocation = ""
            originalImageName = "EmptyFileName"
            ext = ""
    
    # Attempt to get the title text (if unavailable, use originalImageName)
    try:
        imageTitleText = imageTitle[0].text
    except:
        print("  Image title not found, substituting original image filename")
        imageTitleText = originalImageName

    # Name the output image file based on the imageNameType toggle
    if imageNameType == "title":
        # Set image save name to be the comic title
        imgSaveName = imageTitleText
    elif imageNameType == "originalFilename":
        # Set image save name to original image name (based on URL)
        imgSaveName = originalImageName
    print("  Comic Title: " + imageTitleText)
    
    # Lets quickly remove any characters from that title that may cause issues later
    imgSaveName = sanitizeString(imgSaveName)

    # Prior to building the file paths (and resetting it), lets make note of the name of the previous file
    # If it exists, make a nice link to it to use when we make the HTML page later, if not, indicate we are at the current page
    if txtSavePathName == "":
        nextPageHTML = "CURRENT"
    else:
        nextPageHTML = "<a href=\"" + txtSavePathName + "\">Next</a>"

    # Build the final file path for the image using the output dir, the image name, and the image extension
    if getImage == "True":
        # Double check that we actually found an image in the page
        if imageLocation != "":
            imgSavePathFull = os.path.join(outputPath, imgSaveName + ext)
        else:
            # If we didn't find an image, build an informative save path (to make a blank file)
            imgSavePathFull = os.path.join(outputPath, imgSaveName + " (Image not found on site)" + ext)
    # Build a similar file path for the text content
    txtSavePathFull = os.path.join(outputPath, imgSaveName + ".html")
    txtSavePathName = imgSaveName + ".html"

    # check against the cached imageLocation to see if we successfully found a new image. If not, break
    if mostRecentImageURL == imageLocation:
        print("\nScript failed to find images twice in a row. We've hit an error!")
        break

    # If the user requested we get the comic image
    if (getImage == "True") and (imageLocation != ""):       
        print("  Saving: " + imageLocation + "\n  To path: " + imgSavePathFull)
        # If the image file we are about to write doesn't already exist...
        if not os.path.isfile(imgSavePathFull):
            # Since we will try to save the image, reset the consecutiveSkipCount to zero
            consecutiveSkipCount = 0

            # Write out the image file with the imgSavePathFull we built and the imageLocationn we found
            with open(imgSavePathFull, 'wb') as workingFile:
                response = requests.get(imageLocation, stream=True)

                # If the image response is fine (200), download it
                if response.ok:
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        workingFile.write(block)
                    workingFile.close()
                    print("  Image saved.")
                # Alternate download method to try if the image response itself also yields a 406 error
                elif response.status_code == 406:
                    r = urllib.request.urlopen(imageLocation)
                    workingFile.write(r.read())
                    print("  Image saved. (despite 406 response)")
                else:
                    print ("  Error saving image: " + response.text)

        else:
            print("  Found existing Image. skipped.")
            consecutiveSkipCount = consecutiveSkipCount + 1
    elif (imageLocation == ""):
        print("  Placeholder file created in place of missing image!")
        open(imgSavePathFull, 'a').close()
    
    # Clear out javascript warning from comment, if it is present
    comicCommentHTML = comicCommentHTML.replace("<noscript>Javascript is required to view this site. Please enable Javascript in your browser and reload this page.</noscript>","")
    
    # If the user has requested we build an nice HTML page for the output
    if (buildHTML == "True"):
        
        # Build the html string with the image, a link to the page online, the author comment if requested, and a link to the next page (previous page scraped)
        htmlStyle = "<style>body {background-color: #cccccc}</style>"
        htmlNav = "<a href=\"" + currentPageURL + "\">" + imageTitleText + "</a> | " + nextPageHTML
        htmlImg = "<img src=\"" + imgSaveName + ext + "\">"
        htmlTableStart = "<table width=\"70%\" style=\"margin-left:auto;margin-right:auto;\"><tr><td>"
        htmlTableEnd = "</td></tr></table>"
        # Combine html parts to make full string
        textStr = htmlStyle + "<center>" + htmlNav + "<br>" + htmlImg + "<br>" + htmlNav + "<br></center>" + htmlTableStart + comicCommentHTML + htmlTableEnd

        # If the file exists, and we haven't overwritten one yet, continue (This makes sure the latest page has a valid "Next" link)
        if (os.path.isfile(txtSavePathFull) and (overwriteCount < 1)):
            # Write out a txt file with the comic title and author comment (and source URL) to the txtSavePathFull we built
            with open(txtSavePathFull, 'w', encoding="utf-8") as workingFile:
                workingFile.write(textStr)
                workingFile.close()
                print("  Found existing page. Overwritten.")
                overwriteCount += 1
        elif not os.path.isfile(txtSavePathFull):
            # Write out a txt file with the comic title and author comment (and source URL) to the txtSavePathFull we built
            with open(txtSavePathFull, 'w', encoding="utf-8") as workingFile:
                workingFile.write(textStr)
                workingFile.close()
                print("  Page saved.")
        elif os.path.isfile(txtSavePathFull):
            print("  Found existing page. Skipped.")

    # Time to try and navigate to the next page!

    # Get the element that is the next button
    nextButton = driver.find_elements_by_xpath(nextButtonPath)
    
    # If we found no matching (nextbutton) elements, break out of the loop
    if len(nextButton) < 1:
        print("\nNo next/previous page button found on this page.\nWe've likely hit the end!")
        break
    
    #cascade cache the current URL to check against after we attempt to move to the next page (helps detect loops)
    secondMostRecentURL = mostRecentURL
    mostRecentURL = driver.current_url
    mostRecentImageURL = imageLocation
    
    # If the nextButtonType is a basic link, parse it out of the element and attempt to navigate there
    if nextButtonType == "link":
        nextButtonURL = nextButton[0].get_attribute('href')
        currentPageURL = nextButtonURL
        
        # First try requesting the webpage and make sure it returns a good status code
        # If the attempt itself fails, return that error
        pageStatus = validLinkCheck(nextButtonURL)
        # If the request was good, let the user know, if it was anything else, pass that error to the user and break
        if (pageStatus == "Good"):
            # Nice! The page exists and returns a good code
            print('\nAccessing page: ' + nextButtonURL)
        else:
            # If we can't find the current page (or the attempt itself failed), let the user know and break out of the while loop
            print('\nNext page unavailable: ' + str(nextButtonURL) + "\n  Request yielded: " + pageStatus)
            break
        # If we didn't break, let's open it in Gecko to start our parsing
        driver.get(nextButtonURL)
        
    # If the nextButtonType is javaClick, instead of parsing the next object, just click it
    elif nextButtonType == "javaClick":
        javaNextButton = nextButton[0].click()
        print('\nAccessing page: ' + driver.current_url)
        # This sleep alleviates a scenario where the javaClick could cycle a page
        # without giving the page time to actually respond,
        # resulting in an infinite cycle of incrementing, blanks pages. ().o
        time.sleep(1.5)
    
    # Check against the cached urls to see if we successfully advanced a page. If not, break
    if mostRecentURL == driver.current_url:
        print("\nScript not successfully advancing pages (stuck).\nWe've either hit the current page or an error!")
        break
    if secondMostRecentURL == driver.current_url:
        print("\nScript not successfully advancing pages (looping).\nWe've likely hit an error!")
        break

    # Check how many images we've skipped. If it's over 5, break
    if (consecutiveSkipCount >= 5):
        print("\nScript has skipped 5 consecutive image downloads.\nWe've likely reached existing archived content!")
        break

# Close browser
driver.close()

print("\nAll available pages scraped. Exiting.")










