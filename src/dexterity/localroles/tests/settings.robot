*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  Products/PasswordStrength/tests/common.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Test Setup  Test Setup
Test Teardown  Close all browsers

*** Test Cases ***

Test local roles dexterity form
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    # check form is empty
    ${state1} =  Get selected list value  id=form-widgets-localroleconfig-AA-widgets-state
    Should be equal  ${state1}  pending
    Element should contain  id=form-widgets-localroleconfig-AA-widgets-value  ${EMPTY}
    Checkbox should not be selected  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Contributor"]
    Checkbox should not be selected  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Editor"]
    Checkbox should not be selected  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Owner"]
    Checkbox should not be selected  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Reader"]
    Checkbox should not be selected  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Reviewer"]
    # fill form
    Select from list by value  css=#form-widgets-localroleconfig-AA-widgets-state  private
    Input text  id=form-widgets-localroleconfig-AA-widgets-value  cavemans
    Select checkbox  css=#formfield-form-widgets-localroleconfig-AA-widgets-roles input[value="Reader"]
    Click button  id=form-buttons-apply
    # Redirected
    Debug
    Element should contain  id=form-widgets-localroleconfig-AA-widgets-value  cavemans

*** Keywords ***
Test Setup
    Open SauceLabs test browser
    Go to  ${PLONE_URL}
    Enable autologin as  Manager
