Feature: Backend Flask App - Login
	In order to protect directory
	As a system
	I want users to have to login

	    Scenario: Successful Login
        Given the app is running
        When I pass valid credentials to the login endpoint
        Then the response of "200" and "Logged in successfully" should be returned
        And cookies should be set

    Scenario: Unsuccessful Login - Incorrect username and password
        Given the app is running
        When I pass an incorrect username and password to the login endpoint
        Then the response of "401" and "The username you entered cannot be identified." should be returned

    Scenario: Unsuccessful Login - Incorrect password
        Given the app is running
        When I pass an incorrect password to the login endpoint
        Then the response of "401" and "The password you entered was incorrect." should be returned

    Scenario: Unsuccessful Login - Incorrect username
        Given the app is running
        When I pass an incorrect username to the login endpoint
        Then the response of "401" and "The username you entered cannot be identified." should be returned

    Scenario: Unsuccessful Login - Missing password
        Given the app is running
        When I pass only a username to the login endpoint
        Then the response of "400" and "Missing username or password" should be returned

    Scenario: Unsuccessful Login - Missing username
        Given the app is running
        When I pass only a password to the login endpoint
        Then the response of "400" and "Missing username or password" should be returned

    Scenario: Unsuccessful Login - Missing username and password
        Given the app is running
        When I pass no credentials to the login endpoint
        Then the response of "400" and "Missing username or password" should be returned

    Scenario: Unsuccessful Login - Invalid JSON Format in Request
        Given the app is running
        When I pass data in an invalid JSON format to the login endpoint
        Then the response of "400" and "Invalid request format" should be returned

    Scenario: Server Error During Login Process
        Given the app is running
        When I pass valid credentials but the server encounters an internal error during login
        Then the response of "500" and the specific error message should be returned

    Scenario: Already Logged In
        Given the app is running
        And the user is already logged in
        When I pass valid credentials to the login endpoint again
        Then the response of "200" and "Already logged in" should be returned

    Scenario: Session Cookie Attributes Verification
        Given the app is running
        When I pass valid credentials to the login endpoint
        Then the response should include a 'Set-Cookie' header with 'user_session' cookie
        And the cookie should have 'HttpOnly' and 'Secure' attributes set
