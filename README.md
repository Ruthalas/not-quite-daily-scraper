# not-quite-daily-scraper
>A simple scraper for simple webcomics. 

Download images and comment sections with ease, utilizing a simple config file.

Included example is for the '(not quite) Daily Comic'.

Currently under development.

## Setup

Download repo

Install the following dependencies:
* selenium (pip3 install selenium)
 
Download the following dependencies to the project folder:
* geckoDriver (https://github.com/mozilla/geckodriver/releases)
 
## Usage
Create and fill out a config file for each comic you want to scrape.

The key pieces of info are the xpaths to the comic's image, title, and next button

Then run:

```
python scraper.py NQDC-Config.txt
```
 
## Psuedocode

* Gather variables from config file
* Open headless firefox instance with selenium
* Loop through pages, setting each new page based on the 'next' link
    * Gather relevant page elements
    * Extract data from page elements
    * Compose output paths
    * Save content out to file