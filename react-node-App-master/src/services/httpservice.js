var Fetch = require('whatwg-fetch');
var baseUrl = 'http://localhost:6060';

var service = {
  get: function (url) {
    return fetch(baseUrl + url)
    .then(function(response) {
      return response.json();
    });
  },
  post: function (url,body) {

    fetch(baseUrl + url,{
      method: 'post',
      headers: new Headers({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }),
      body: JSON.stringify(body)
    });
  }
}

module.exports = service;
