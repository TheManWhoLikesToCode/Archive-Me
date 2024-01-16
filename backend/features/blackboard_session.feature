Feature: Blackboard Session Management

  Scenario: Valid credentials login
    Given I have valid credentials
    When I login
    Then the response should be "Login successful."

  Scenario: Invalid both username and password
    Given I have invalid username and password
    When I login
    Then the response should be "The username you entered cannot be identified."

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
