module.exports = {
  seconds: function(val) { return val},
  minutes: function(val) { return val * (60) },
  hours:   function(val) { return val * (60*60) },
  days:    function(val) { return val * (24*60*60) },
  weeks:   function(val) { return val * (7*24*60*60) },
  years:   function(val) { return val * (365*24*60*60)} 
};