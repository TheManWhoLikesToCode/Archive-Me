Feature: Blackboard Session - Get Download Tasks
    In order to return the courses to the user
    As a system
    I want to get the download tasks

Scenario: Get download tasks when logged in
    Given I have valid credentials
    And I am logged in
    When I get download tasks
    Then the get download tasks response should be "Download tasks retrieved"

  Scenario: Get download tasks when not logged in
    Given I have invalid username and password
    And I am not logged in
    When I get download tasks
    Then the get download tasks response should be "Not logged in."