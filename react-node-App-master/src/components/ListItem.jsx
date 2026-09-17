var React = require('react');
var ListItem = React.createClass({
  render: function () {
    return (
      <li id={this.props.key}>
        <h4>{this.props.ingredient}</h4>
      </li>
    );
  }
});

module.exports = ListItem;
