# not-quite-daily-scraper
>A simple scraper for simple webcomics. 

Download comic images and author comments with ease, utilizing a simple config file.

Output either just images or HTML pages with built in navigation. (just images currently under development!)

Included example config is for the '(not quite) Daily Comic'.

Currently under development. Developed for Windows.

## Setup

Download repo

Install the following dependencies:
* selenium (pip3 install selenium)
 
Download the following dependencies and install them to PATH (Windows):
* geckoDriver (https://github.com/mozilla/geckodriver/releases)
 
## Usage
Create and fill out a config file for each comic you want to scrape.
If you choose to use the HTML option (currently force-enabled, under construction) it is advised to start at the current page and iterate backwards to allow the script to link each page to the next.

Settings/Configurables include:

* Output Path (leave blank to use project directory)
* Create Subfolder? (if enabled, creates subdir based on comic name)
* Download Comments?
* Download Image?
* Image Naming (chose to base on either comic title or on original image name)
* Run Headless? (run without showing the browser window- disable for troubleshooting)
* Comic Name
* comicStartPage (XPATH)
* imageTitlePath (XPATH)
* nextButtonPath (XPATH)
* nextButtonType (accepts either link or javaClick, representing whether the button has an href or must be clicked)
* imagePath (XPATH)
* commentPath (XPATH)
* initialClick (XPATH, runs once at start- can be used to start at homepage, then click latest page link)

Then run:

```
python scraper.py My-Config.txt
```
 
## Psuedocode

* Check if config file exists
* Gather variables from config file
* Build output directory path, and create it if it does not exist
* Configure and open headless firefox instance with selenium
* Check if starting page is valid
* If user requested it, click the provided initialClick element
* Loop through pages, setting each new page based on the 'next' link
    * Gather relevant page elements
    * Extract data from page elements
    * Compose output paths and names
    * Sanitise paths and names
    * Save image (if requested)
    * Save comment (if requested)
    * Record the current/previous page
    * Click the next button to proceed to new page
    * Check against recorded recent pages to confirm we aren't stuck in a loop
* ....Profit!