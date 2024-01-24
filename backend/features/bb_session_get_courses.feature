Feature: Blackboard Session - Get Courses
    In order to archive courses for the user 
    As a system
    I want to get courses

Scenario: Get courses when logged in
    Given I have valid credentials
    And I am logged in
    When I get courses
    Then the get courses response should be "Courses retrieved"

  Scenario: Get courses when not logged in
    Given I have invalid username and password
    And I am not logged in
    When I get courses
    Then the get courses response should be "Not logged in."