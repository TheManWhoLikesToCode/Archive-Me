Feature: Blackboard Session Management

  Scenario: Creating a new blackboard session for a user
    Given a blackboard session manager
    When I request a session for user "Alice"
    Then a new session should be created for "Alice"

  Scenario: Retrieving an existing blackboard session for a user
    Given a blackboard session manager
    And an existing session for user "Bob"
    When I request a session for user "Bob"
    Then the existing session for "Bob" should be returned

  Scenario: Storing a blackboard session for a user
    Given a blackboard session manager
    And a blackboard session for user "Charlie"
    When I store the session for user "Charlie"
    Then the session for "Charlie" should be stored in the manager

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

  Scenario: Deleting a blackboard session for a user
    Given a blackboard session manager
    And an existing session for user "Eve"
    When I delete the session for user "Eve"
    Then the session for "Eve" should be removed

  Scenario: Cleaning up inactive sessions
    Given a blackboard session manager
    And inactive sessions older than 3600 seconds
    When I clean up inactive sessions
    Then all sessions older than 3600 seconds should be removed

  Scenario: Attempting to retrieve a session for a non-existent user
    Given a blackboard session manager
    When I retrieve a session by username "NonExistentUser"
    Then no session should be returned

  Scenario: Attempting to retrieve a session with a non-existent session ID
    Given a blackboard session manager
    When I retrieve a session by session ID "nonExistentSession123"
    Then no session should be returned

  Scenario: Attempting to delete a session for a non-existent user
    Given a blackboard session manager
    When I delete the session for user "NonExistentUser"
    Then no session should be removed

  Scenario: Cleaning up with no inactive sessions
    Given a blackboard session manager
    And no inactive sessions
    When I clean up inactive sessions
    Then no session should be removed

  Scenario: Updating the last activity time of a session
    Given a blackboard session manager
    And an existing session for user "George"
    When I update the last activity time for "George"'s session
    Then the last activity time for "George"'s session should be updated

  Scenario: Multiple users sharing the same session ID
    Given a blackboard session manager
    And an existing session with ID "sharedSession123" for users "Harry" and "Irene"
    When I retrieve a session by session ID "sharedSession123"
    Then the same session should be returned for both "Harry" and "Irene"