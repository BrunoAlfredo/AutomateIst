import time
import sys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def clickOnAButton(*args, iDriver, iSleepTime):
  aButton = iDriver
  for aArg in args:
    aButton = aButton.find_element_by_id(aArg)
  aButton.click()
  time.sleep(iSleepTime)

def authenticationProcedure(iDriver):
  usernameField = iDriver.find_element_by_id("username")
  usernameField.send_keys("")
  passwordField = iDriver.find_element_by_id("password")
  passwordField.send_keys("")
  aIDs = ["submit-istid"]
  clickOnAButton(iDriver=iDriver, iSleepTime=1, *aIDs)
  print("\n------LOGIN Performed")

def logoutProcedure(iDriver):
  aIDs = ["rcmbtn108"]
  clickOnAButton(iDriver=iDriver, iSleepTime=1, *aIDs)
  print("\n------LOGOUT Performed")

def readRulesFromFile(iFileName):
  print("\n------Loading Rules")
  aSetOfRules = []
  with open(iFileName,'r') as aReader:
    for aLine in aReader:
      aRule = tuple(aLine[0:-1].split(", "))
      aSetOfRules.append(aRule)
  print(aSetOfRules)
  return aSetOfRules

def selectLastPageOfMessages(iDriver):
  print("\n------Last page of messages requested")
  aIDs = ["messagelistfooter", "rcmbtn137"]
  clickOnAButton(iDriver=iDriver, iSleepTime=2.5, *aIDs)

def selectPreviousPageOfMessages(iDriver):
  print("\n------Previous page of messages requested")
  aIDs = ["messagelistfooter", "rcmbtn135"]
  clickOnAButton(iDriver=iDriver, iSleepTime=2.5, *aIDs)

def moveOneMessage(iDriver, iDestination):
  aIDs = ["messagemenulink"]
  clickOnAButton(iDriver=iDriver, iSleepTime=1, *aIDs)

  aIDs = ["messagemenu", "rcmbtn127"]
  clickOnAButton(iDriver=iDriver, iSleepTime=1, *aIDs)

  aFolderOptions = iDriver.find_element_by_id("folder-selector"). \
                    find_element_by_tag_name("ul"). \
                    find_elements_by_tag_name("li")

  for aFolderOption in aFolderOptions:
    aOptionName = aFolderOption.find_element_by_tag_name("a").text
    if (aOptionName == iDestination):
      aFolderOption.click()
      time.sleep(0.5)
      return

def processOneMessage(iDriver, iMessage, iSetOfRules):
  aSender = iMessage.find_element_by_class_name("fromto").text
  print(aSender)
  aSubject = iMessage.find_element_by_class_name("subject").text
  print("  ** " + aSubject)

  for aRule in iSetOfRules:
    if (aRule[0] in aSender):
      print("    ---> Moved message to " + aRule[1])
      moveOneMessage(iDriver, aRule[1])
      return True
  print("    ---> OUT OF THE RULES ")
  time.sleep(1)
  return False

def processOnePageOfMesssages(iDriver, aSetOfRules):
  print("\n------Processing one page of messages")

  aBoxOfMessages = iDriver.find_element_by_id("messagelist")
  aMessagesList = aBoxOfMessages.find_elements_by_tag_name("tr")

  isMessageMoved = False
  actions = ActionChains(iDriver)
  actions.move_to_element(aMessagesList[1]).click().perform()
  isMessageMoved = processOneMessage(iDriver, aMessagesList[1], aSetOfRules)
  for aMessage in aMessagesList[2:]:
    actions = ActionChains(iDriver)
    if (isMessageMoved):
      actions.move_to_element(aMessage).click().perform()
    else:
      actions.send_keys(Keys.ARROW_DOWN).perform()
    isMessageMoved = processOneMessage(iDriver, aMessage, aSetOfRules)


"""Robot Starts --- MAIN """
aDriver = webdriver.Firefox()
aDriver.get("https://id.tecnico.ulisboa.pt/cas/login?service=https%3A%2F%2Fwebmail.tecnico.ulisboa.pt%2Frc%2F%3F_task%3Dmail%26_action%3Dlogin")

authenticationProcedure(aDriver)
aSetOfRules = readRulesFromFile("rules.txt")
selectLastPageOfMessages(aDriver)

numberOfPagesToClean = 1
if (len(sys.argv) > 1):
  numberOfPagesToClean = int(list(sys.argv)[-1])
for i in range(0,numberOfPagesToClean):
  processOnePageOfMesssages(aDriver, aSetOfRules)
  selectPreviousPageOfMessages(aDriver)

logoutProcedure(aDriver)
aDriver.close()
