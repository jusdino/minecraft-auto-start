/*
 * This app, even for local dev, does not use this file. It is replaced with an environment file generated
 * with `node run generate-env`, which takes the environment variables listed below and places them in
 * an environment object shaped like below.
 */
export const environment = {
  awsProjectRegion: process.env['MAS_AWS_PROJECT_REGION'],
  awsCognitoRegion: process.env['MAS_AWS_COGNITO_REGION'],
  awsUserPoolId: process.env['MAS_USER_POOL_ID'],
  awsUserPoolWebClientId: process.env['env.MAS_WEB_CLIENT_ID'],
  domain: process.env['MAS_OAUTH_DOMAIN'],
  redirectSignIn: process.env['MAS_REDIRECT_SIGN_IN'],
  redirectSignOut: process.env['MAS_REDIRECT_SIGN_OUT'],
};
