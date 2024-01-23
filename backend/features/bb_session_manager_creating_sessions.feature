Feature: Blackboard Sesssion Manager - Creating a new session for a user
    In order to use blackboard
    As a user
    I want to create a new session

  Scenario: Creating a new blackboard session for a user
    Given a blackboard session manager
    When I request a session for user "Alice"
    Then a new session should be created for "Alice"
    
  Scenario: Storing a blackboard session for a user
    Given a blackboard session manager
    And a blackboard session for user "Charlie"
    When I store the session for user "Charlie"
    Then the session for "Charlie" should be stored in the manager