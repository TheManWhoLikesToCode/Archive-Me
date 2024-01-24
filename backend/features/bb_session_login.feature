Feature: Blackboard Session - Login
    In order to access Blackboard
    As a system
    I want to login
    
Scenario: Valid credentials login
    Given I have valid credentials
    When I login
    Then the response should be "Login successful."

  Scenario: Invalid both username and password
    Given I have invalid username and password
    When I login
    Then the response should be "The username you entered cannot be identified."

  Scenario: I attempt to login when already logged in
    Given I have valid credentials
    And I am logged in
    When I login
    Then the response should be "Already logged in."