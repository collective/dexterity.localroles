*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Test Setup  Test Setup
Test Teardown  Close all browsers

*** Variables ***
${first_row_xpath} =    xpath=//table[@class="datagridwidget-table-view"]/tbody/tr[1]
${state_xpath} =        ${first_row_xpath}/td[1]/select
${value_xpath} =        ${first_row_xpath}/td[2]/input
${contributor_xpath} =  ${first_row_xpath}/td[3]/span/span[1]/input

*** Test Cases ***

Test local roles dexterity form
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    # check form is empty
    List selection should be  ${state_xpath}  pending
    Element should contain  ${value_xpath}  ${EMPTY}
    Checkbox should not be selected  ${contributor_xpath}
    # fill form
    Select from list by value  ${state_xpath}  private
    Input text  ${value_xpath}  cavemans
    Select checkbox  ${contributor_xpath}
    Click button  id=form-buttons-apply
    Submit form  css=div#content form
    # Redirected
    List selection should be  ${state_xpath}  private
    TextField value should be  ${value_xpath}  cavemans
    Checkbox should be selected  ${contributor_xpath}

*** Keywords ***
Test Setup
    Open SauceLabs test browser
    Go to  ${PLONE_URL}
    Enable autologin as  Manager
