var proxyMiddleware = require('http-proxy-middleware');

const PROXY_CONFIG = [
  {
      context: [
        "!/ui/**"
      ],
      target: "http://localhost:8080",
      secure: false,
      "logLevel": "debug"
  }
];

module.exports = PROXY_CONFIG;

