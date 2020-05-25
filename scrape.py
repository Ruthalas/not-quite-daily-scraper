# Import modules we will be using
import configparser
from selenium import webdriver

# Pull in variables from config file
configparser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configparser.read(configFilePath)

comicName = configparser.get('Comic', 'comicName')
commentPath = configparser.get('Comic', 'commentPath')

# Set up the browser we'll be using
driver = webdriver.Firefox()
# fetch webpage
driver.get("https://www.truefork.org/Art/comic/cindex.php?44")

# Grab comment
comicComment = driver.find_elements_by_xpath(commentPath)


print(comicComment)



