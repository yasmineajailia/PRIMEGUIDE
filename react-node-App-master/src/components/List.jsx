var React = require('react');
var ListItem = require('./ListItem.jsx');



var List = React.createClass({
  getInitialState: function () {
    return {items:[]};
  },
  render: function () {
    var listItem =  this.props.items.map(function (items) {
      return (
        <ListItem id={items.id} ingredient={items.text} />
      );
    });

    return (
      <ul>{listItem}</ul>
    );
  }
});

module.exports = List;
