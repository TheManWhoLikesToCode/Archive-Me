Feature: Blackboard session management - Modifying users sessions
    In order to modify users sessions to keep them alive
    As a blackboard administrator
    I want to be able to modify users sessions

  Scenario: Updating the last activity time of a session
    Given a blackboard session manager
    And an existing session for user "George"
    When I update the last activity time for "George"'s session
    Then the last activity time for "George"'s session should be updated
