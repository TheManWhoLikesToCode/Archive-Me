Feature: Backend Flask App - Login
	In order to protect directory
	As a system
	I want users to have to login

	Scenario: Successful Login
		Given App is running
		When I pass valid credentials to the login endpoint
		Then The response of "200" and "Logged in Successfully" should be returned

    Scenario: Unsuccessful Login - Incorrect username and password
        Given App is running
        When I pass an incorrect username and password to the login endpoint
        Then The response of "401" and "The username you entered cannot be identified." should be returned

    Scenario: Unsuccessful Login - Incorrect password
        Given App is running
        When I pass an incorrect password to the login endpoint
        Then The response of "401" and "The password you entered was incorrect." should be returned

    Scenario: Unsuccessful Login - Incorrect username
        Given App is running
        When I pass an incorrect username to the login endpoint
        Then The response of "401" and "The username you entered cannot be identified." should be returned