define('app/visualization/components/bar-chart/bar-chart' ,['require','knockout', 'c3', 'd3', '$http', 'q', 'text!app/templates/visualization/bar.html'], function(require, ko, c3, d3, $http, $q, template) {
  'use strict';

  function compare(a,b) {
    a = parseInt(a._id);
    b = parseInt(b._id);
    if (a < b) {
      return -1;
    }
    else if (a > b) {
      return 1;
    }
    else {
      return 0;
    }
  }

  function clone(obj) {
    if (null === obj || 'object' !== typeof obj) {
      return obj;
    }
    var copy = obj.constructor();
    for (var attr in obj) {
      if (obj.hasOwnProperty(attr)) {
        copy[attr] = obj[attr];
      }
    }
    return copy;
  }

  function mergeDublicateYears(list) {
    var listCopy = list.slice();
    var temp = {};
    var obj = null;
    for(var i=0; i < listCopy.length; i++) {
      obj=listCopy[i];

      if(!temp[obj._id]) {
        temp[obj._id] = obj;
      } else {
        temp[obj._id].count += obj.count;
      }
    }
    var result = [];
    for (var prop in temp) {
      result.push(temp[prop]);
    }
    return result;
  }

  function ViewBar() {
    var self = this;
    this.usePercentage = ko.observable(false);
    var total = [];
    var initFavor = [];
    var favor = [];
    var favorPerc = [];
    var initAgainst = [];
    var against = [];
    var againstPerc = [];
    var initNone = [];
    var none = [];
    var nonePerc = [];

    self.alert = ko.observable(0);
    self.alertMsg = ko.observable('Error retrieving some of the data!');
    self.progress = ko.observable(5);
    self.progressPct = ko.observable('5%');
    console.log(self.progress());

    var favorReq = $http.get('https://ieccs.herokuapp.com/api/stance/year/FAVOR')
      .success(function(data) {
        initFavor = data;
        self.progress(self.progress()+30);
        self.progressPct(self.progress()+'%');
        console.log(self.progress());
      })
      .error(function(err) {
        self.alert(1);
        console.log(err);
      });
    var againstReq = $http.get('https://ieccs.herokuapp.com/api/stance/year/AGAINST')
      .success(function(data) {
        initAgainst = data;
        self.progress(self.progress()+30);
        self.progressPct(self.progress()+'%');
        console.log(self.progress());
      })
      .error(function(err) {
        self.alert(1);
        console.log(err);
      });
    var noneReq = $http.get('https://ieccs.herokuapp.com/api/stance/year/NONE')
      .success(function(data) {
        initNone = data;
        self.progress(self.progress()+30);
        self.progressPct(self.progress()+'%');
        console.log(self.progress());
      })
      .error(function(err) {
        self.alert(1);
        console.log(err);
      });

    $q.all([favorReq, noneReq, againstReq]).then( function() {
      self.progress(self.progress()+5);
      self.progressPct(self.progress()+'%');
      console.log(self.progress());

      setTimeout(function(){
        self.progress(self.progress()+1);
        self.progressPct(self.progress()+'%');
        console.log(self.progress());
      }, 500);


      initFavor = initFavor.sort(compare);
      initNone = initNone.sort(compare);
      initAgainst = initAgainst.sort(compare);

      initFavor = mergeDublicateYears(initFavor);
      initAgainst = mergeDublicateYears(initAgainst);
      initNone = mergeDublicateYears(initNone);


      for (var i= 0; i<initFavor.length;i++){
        total.push(clone(initFavor[i]));
      }
      for (i= 0; i<initAgainst.length;i++){
        total.push(clone(initAgainst[i]));
      }
      for (i= 0; i<initNone.length;i++){
        total.push(clone(initNone[i]));
      }

      total = mergeDublicateYears(total);

      total.forEach(function (item) {
        initFavor.filter(function (obj) {
          if (obj._id === item._id) {
            var percent = parseFloat(obj.count / item.count);
            obj.percent = Math.round(percent * 10000)/100;          }
        });
        initNone.filter(function (obj) {
          if (obj._id === item._id) {
            var percent = parseFloat(obj.count / item.count);
            obj.percent = Math.round(percent * 10000)/100;          }
        });
        initAgainst.filter(function (obj) {
          if (obj._id === item._id) {
            var percent = parseFloat(obj.count / item.count);
            obj.percent = Math.round(percent * 10000)/100;
          }
        });
      });

      favorPerc.push('Favor');
      favorPerc = favorPerc.concat(initFavor.map(function (a) {return a.percent;}));

      againstPerc.push('Against');
      againstPerc = againstPerc.concat(initAgainst.map(function (a) {return a.percent;}));

      nonePerc.push('None');
      nonePerc = nonePerc.concat(initNone.map(function (a) {return a.percent;}));

      favor.push('Favor');
      favor = favor.concat(initFavor.map(function (a) {return a.count;}));

      against.push('Against');
      against = against.concat(initAgainst.map(function (a) {return a.count;}));

      none.push('None');
      none = none.concat(initNone.map(function (a) {return a.count;}));

      var keys = [];
      keys = initFavor.map(function (a) {return parseInt(a._id);});

      var chart = c3.generate({
        bindto: '#BarChart',
        data: {
          columns: [
            favor,
            against,
            none
          ],
          type: 'bar',
          groups: [
            ['Favor', 'Against', 'None']
          ]
        },
        grid: {
          y: {
            lines: [{value:0}]
          }
        },
        axis: {
          x: {
            label: {
              text: 'Year',
              position: 'outer-center'
            },
            type: 'category',
            categories: keys
          }
        }
      });

      self.usePercentage.subscribe(function(newValue) {
        if (newValue) {
          chart.load({
            columns: [favorPerc, againstPerc, nonePerc]
          });
        } else {
          chart.load({
            columns: [favor, against, none]
          });
        }
      });

      self.updateStanceStatus = function(index, visModel)  {
        console.log('progress = ' + this.progress());
        updateBar(5, self);
        self.stanceModel.forEach(function(item) {
          if (index === item.id) {
            item.status(true);
            console.log('Requesting..');
            updateBar(50, self);
            requestData(item.type, visModel.type, self);
            self.allStancesFalse(false);
          }
          else {
            item.status(false);
          }
        });
      };
    });
  }

  return {
    viewModel: ViewBar,
    template: template
  };
});
