# not-quite-daily-scraper
>A simple scraper for simple webcomics. 

Download comic images and author comments with ease, utilizing a simple config file.

Included example is for the '(not quite) Daily Comic'.

Currently under development. Developed for Windows.

## Setup

Download repo

Install the following dependencies:
* selenium (pip3 install selenium)
 
Download the following dependencies and install them to PATH (Windows):
* geckoDriver (https://github.com/mozilla/geckodriver/releases)
 
## Usage
Create and fill out a config file for each comic you want to scrape.

Settings/Configurables include:
* Output Path (leave blank to use project directory)
* Create Subfolder? (if enabled, creates subdir based on comic name)
* Download Comments?
* Download Image?
* Image Naming (based on comic strip title or original image name)
* Run Headless? (run without showing the browser window- disable for troublshooting)

* Comic Name
* comicStartPage (XPATH)
* imageTitlePath (XPATH)
* nextButtonPath (XPATH)
* nextButtonType (accepts either link or javaClick, representing whether the button has an href or must be clicked)
* imagePath (XPATH)
* commentPath (XPATH)
* initialClick (XPATH, can be used to start at the comic's homepage and click into the latest page link)

Then run:

```
python scraper.py NQDC-Config.txt
```
 
## Psuedocode

* Gather variables from config file
* Build output directory path, and create it if it does not exist
* Open headless firefox instance with selenium
* Loop through pages, setting each new page based on the 'next' link
    * Gather relevant page elements
    * Extract data from page elements
    * Compose output paths
    * Save content out to file