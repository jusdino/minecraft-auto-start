import { environment } from "./environments/environment";

const awsconfig = {
  awsProjectRegion: environment.awsProjectRegion,
  awsCognitoRegion: environment.awsCognitoRegion,
  awsUserPoolId: environment.awsUserPoolId,
  awsUserPoolWebClientId: environment.awsUserPoolWebClientId,
  oauth: {
    domain: environment.domain,
    scope: [
      'phone',
      'email',
      'openid',
      'profile',
      'aws.cognito.signin.user.admin'
    ],
    redirectSignIn: environment.redirectSignIn,
    redirectSignOut: environment.redirectSignOut,
    responseType: 'code'
  }
};

export default awsconfig;
