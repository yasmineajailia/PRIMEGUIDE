var React = require('react');
var List = require('./List.jsx');
var HTTP = require('../services/httpservice');

//this class can recieve user input there are things we need to handle
var ListManager = React.createClass({
    getInitialState: function () {
      return {items:[],newItemText:''};
    },
    componentWillMount: function () {
      HTTP.get('/')
      .then(function (data) {
        this.setState({items:data});
      }.bind(this));
      console.log(this.state.items);
    },
    onChange: function (ele) {
      this.setState({newItemText:ele.target.value});
    },
    handleSubmit: function (ele) {
      //preventDefault: to prevent onclick ->we are using html form submit
      ele.preventDefault();
      var currentItems = this.state.items;
      var newItem;
      if(currentItems.length>0){
        newItem = {
          "id": (parseInt(currentItems[currentItems.length -1].id) + 1).toString(),
          "text": this.state.newItemText
        };
      }
      else {
        newItem = {
          "id": "0",
          "text": this.state.newItemText
        };
      }
      HTTP.post('/',newItem);
      currentItems.push(newItem);
      this.setState({ items: currentItems, newItemText: '' });
    },
    render: function () {
      var divStyle = {
        marginTop: 20
      };

      var headingStyle = {

      };

      if(this.props.headingColor){
        headingStyle.background = this.props.headingColor;
      }
      return (
        <div className="col-sm-4" style={divStyle}>
          <div className="panel panel-primary">
            <div style={headingStyle} className="panel panel-heading">
              <h3>{this.props.title}</h3>
            </div>
            <div className="panel panel-body">
              <form onSubmit={this.handleSubmit}>
                <div className="row">
                  <div className="col-sm-9">
                    <input className="form-control" onChange={this.onChange} value={this.state.newItemText}></input>
                  </div>
                  <div className="col-sm-2">
                    <button className="btn btn-primary">Add</button>
                  </div>
                </div>
              </form>
            </div>
            <List items={this.state.items}/>
          </div>
        </div>
      );
    }
});


module.exports = ListManager;
