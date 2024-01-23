Feature: Blackboard Session Manager - Deleting Sessions 
      In order to correctly delete user data
      As a system
      I want to delete blackboard sessions
      
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

  Scenario: Attempting to delete a session for a non-existent user
    Given a blackboard session manager
    When I delete the session for user "NonExistentUser"
    Then no session should be removed

  Scenario: Cleaning up with no inactive sessions
    Given a blackboard session manager
    And no inactive sessions
    When I clean up inactive sessions
    Then no session should be removed