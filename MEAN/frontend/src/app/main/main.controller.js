export class SearchController {
  constructor ($http, $compile) {
    'ngInject';
      this.$http = $http;
      this.compile = $compile;
      // this.getMessage();
  }

  query(){
    if(this.searchInput.length <= 0){
      return;
    }
    var vm = this;
    vm.results = null;
    this.$http.get("http://localhost:5000/api/search", {
      params: {queryString: this.searchInput}
    }).then(function(result){
      console.log(result);
      vm.results = result.data;
      console.log(vm.results);
    });
  }

  postMessage(){
    this.$http.post("http://localhost:5000/api/message", {msg: this.message});
  }

  redirect(url){
    if(url){
      $("#infobox").html(url);
      $("#infoboxcol").removeClass("hide");
    }else{
      $("#infobox").html(url);
      $("#infoboxcol").addClass("hide");
    }
    
  }


}
