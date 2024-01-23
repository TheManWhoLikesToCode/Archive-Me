Feature: Blackboard Session - Enable Insturctors and Time 
    In order to correctly name courses
    As a system
    I want to enable instructors and course season
    
  Scenario: Enable instructors when logged in
    Given I have valid credentials
    And I am logged in
    When I enable instructors
    Then the enable instructors response should be "Instructors enabled"

  Scenario: Enable instructors when not logged in
    Given I have invalid username and password
    And I am not logged in
    When I enable instructors
    Then the enable instructors response should be "Not logged in."