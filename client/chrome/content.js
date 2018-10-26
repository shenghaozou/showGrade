chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if( request.message === "clicked_browser_action" ) {
      var regex = new RegExp('project_id=(.*?)&submitter_id=(.*?)$');
      var groups = location.href.match(regex);
      var xmlHttp = new XMLHttpRequest();
      var theUrl = "http://127.0.0.1:5000/" + groups[1] + "/" + groups[2]
      console.log(theUrl)
      xmlHttp.open("GET", theUrl, true);
      xmlHttp.send();
      var result = JSON.parse(xmlHttp.responseText);
      document.getElementById("useremail").innerHTML = result["detail"];
      document.getElementById("general_comments").innerHTML = result["comments"];
    }
  }
);
