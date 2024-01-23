Feature: Blackboard Session Manager: Retrieving a session
    In order to keep track of users 
    As a system
    I want to be able to retrieve a blackboard session for a user

Scenario: Retrieving an existing blackboard session for a user
    Given a blackboard session manager
    And an existing session for user "Bob"
    When I request a session for user "Bob"
    Then the existing session for "Bob" should be returned

  Scenario: Retrieving a blackboard session by username
    Given a blackboard session manager
    And an existing session for user "David"
    When I retrieve a session by username "David"
    Then the session for "David" should be returned

  Scenario: Retrieving a blackboard session by session ID
    Given a blackboard session manager
    And an existing session with ID "session123"
    When I retrieve a session by session ID "session123"
    Then the session with ID "session123" should be returned

  Scenario: Attempting to retrieve a session for a non-existent user
    Given a blackboard session manager
    When I retrieve a session by username "NonExistentUser"
    Then no session should be returned

  Scenario: Attempting to retrieve a session with a non-existent session ID
    Given a blackboard session manager
    When I retrieve a session by session ID "nonExistentSession123"
    Then no session should be returned

  Scenario: Multiple users sharing the same session ID
    Given a blackboard session manager
    And an existing session with ID "sharedSession123" for users "Harry" and "Irene"
    When I retrieve a session by session ID "sharedSession123"
    Then the same session should be returned for both "Harry" and "Irene"