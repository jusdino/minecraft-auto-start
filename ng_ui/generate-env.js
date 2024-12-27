/*
 * Generate an environment file based on environment variables at build time
 */
const fs = require('fs');

const masEnvVarRegex = /^MAS_/i;

const envVars = {};
for (const key in process.env) {
    if (masEnvVarRegex.test(key)) {
    envVars[key] = process.env[key];
    }
}

const environmentFileContent = `export const environment = {
  production: ${process.env.MAS_PRODUCTION === 'true'},
  awsProjectRegion: '${process.env.MAS_AWS_PROJECT_REGION || ''}',
  awsCognitoRegion: '${process.env.MAS_AWS_COGNITO_REGION || ''}',
  awsUserPoolId: '${process.env.MAS_USER_POOL_ID || ''}',
  awsUserPoolWebClientId: '${process.env.MAS_WEB_CLIENT_ID || ''}',
  domain: '${process.env.MAS_OAUTH_DOMAIN || ''}',
  redirectSignIn: '${process.env.MAS_REDIRECT_SIGN_IN || ''}',
  redirectSignOut: '${process.env.MAS_REDIRECT_SIGN_OUT || ''}'
};
`;

fs.writeFileSync('src/environments/environment.cicd.ts', environmentFileContent);
