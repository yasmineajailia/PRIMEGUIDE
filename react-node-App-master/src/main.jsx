//entry point for our app
var React = require('react');
var ReactDom = require('react-dom');
var ListManager = require('./components/ListManager.jsx');

ReactDom.render(<ListManager title="Ingredients"/>,document.getElementById('ingredients'));
