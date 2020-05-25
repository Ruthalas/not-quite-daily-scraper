import configparser

print("YO.")

# Fetch Config
configparser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configparser.read(configFilePath)

print(configparser.get('General', 'outputPath'))
print(configparser.get('General', 'subfolderToggle'))
print(configparser.get('Comic', 'comicName'))

