# not-quite-daily-scraper
>A simple scraper for the simple webcomics. 

Included example is for the '(not quite) Daily Comic'.

Currently under development.

## Setup

Download repo

Install the following dependencies:
* selenium (pip3 install selenium)
 
Download the following dependencies to the project folder:
* geckoDriver (https://github.com/mozilla/geckodriver/releases)
 
## Usage
Fill out the config.txt

The key pieces of info are the xpaths to the comic's image, title, and next button

Then run:

```
python scraper.py
```
 
## Psuedocode

* Gather variables from congif file
* Open headless firefox instance with selenium
* Loop through pages, setting each new page based on the 'next' link
    * Gather relevant page elements
    * Extract data from page elements
    * Compose output paths
    * Save content out to file