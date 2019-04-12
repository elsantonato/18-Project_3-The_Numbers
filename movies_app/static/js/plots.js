// function buildPlot() { 
    /* data route */
// console.log('hello')
var url = "/numbers_data";
d3.json(url).then(function(movies, error) {
  console.log(error);
  console.log(movies);

  var data = [{
    values: movies.TotalGrossAllMovies,
    labels: movies.Distributor,
    type: 'pie'
  }];
  
  var layout = {
    height: 400,
    width: 500
  };
  
  Plotly.newPlot('myDiv', data, layout);

  var data = [{
    x: ["Bohemian Rhapsody", "Widows", "Once Upon a Deadpool", "The Hate U Give"],
    y: [195296306, 42162140, 324574517, 29705000],
    type: 'bar'
  }];
  
  Plotly.newPlot('bar', data);

});
