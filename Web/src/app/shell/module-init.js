define('app/shell/module-init', ['require', '$router', 'knockout'], function(require, router, ko) {
  'use strict';

  function init() {

    ko.components.register('main-nav', {
      require: 'app/shell/components/main-nav'
    });

    router.when('/', {
      viewModelUrl: 'app/shell/home/home',
      templateUrl: 'text!app/templates/home.html'
    }).otherwise({
      redirectTo: '/'
    });
  }

  return {
    init: init
  };
});