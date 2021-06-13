import { CognitoUserPool, AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js';
import * as fetch from 'node-fetch';

global.fetch = fetch;

const poolData = {
    UserPoolId: "us-west-1_0ASwMy5Uf",
    ClientId: "6...i"
 };
 const userPool = new CognitoUserPool(poolData);

 var authenticationDetails = new AuthenticationDetails({
        Username: "jusdino",
        Password: "<temp password>"
 });

 var userData = {
        Username: "jusdino",
        Pool: userPool
 };

 var cognitoUser = new CognitoUser(userData);

cognitoUser.authenticateUser(authenticationDetails, {
    onSuccess: function(result) {
        console.log('access token: ' + result.getAccessToken().getJwtToken());
        console.log('id token: ' + result.getIdToken().getJwtToken());
        console.log('refresh token: ' + result.getRefreshToken().getToken());
    },
    onFailure: function (err) {
        console.log(err);
    },
    newPasswordRequired: function(userAttributes, requiredAttributes) {
        console.log(userAttributes);
        console.log(requiredAttributes);
        cognitoUser.completeNewPasswordChallenge('<new password>', userAttributes, {
            onSuccess: function(result) {
                console.log('password changed');
                console.log(result);
            },
            onFailure: function (err) {
                console.log(err);
            }
        });
    }
});

/*
 { email: 'j...@...l.com' }
    []
password changed
CognitoUserSession {
    idToken: CognitoIdToken {
        jwtToken: 'ey...',
        payload: {
            sub: 'b0a50b19-5c8e-47d0-9f08-f007c3c628eb',
            aud: '66e65v0tsp79dtpm2jt8pkp8vi',
            event_id: 'd01602e0-971f-40e4-a3bb-35e2baa9c834',
            token_use: 'id',
            auth_time: 1617517276,
            iss: 'https://cognito-idp.us-west-1.amazonaws.com/us-west-1_0ASwMy5Uf',
            'cognito:username': 'jusdino',
            exp: 1617520876,
            iat: 1617517276,
            email: 'justinmfrahm@gmail.com'
        }
    },
    refreshToken: CognitoRefreshToken {
        token: 'ey...'
    },
    accessToken: CognitoAccessToken {
        jwtToken: 'ey...',
        payload: {
            sub: 'b0a50b19-5c8e-47d0-9f08-f007c3c628eb',
            event_id: 'd01602e0-971f-40e4-a3bb-35e2baa9c834',
            token_use: 'access',
            scope: 'aws.cognito.signin.user.admin',
            auth_time: 1617517276,
            iss: 'https://cognito-idp.us-west-1.amazonaws.com/us-west-1_0ASwMy5Uf',
            exp: 1617520876,
            iat: 1617517276,
            jti: 'c9b3f157-81d9-4365-918a-d9be288e476e',
            client_id: '6...i',
            username: 'jusdino'
        }
    },
    clockDrift: 0
}
*/