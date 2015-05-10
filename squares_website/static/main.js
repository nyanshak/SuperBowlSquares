
$(function() {
  var year = $('input:hidden[name=year]').val();

  $(".tdhover").hover(function(){
    $(this).addClass("hover");
  }, function(){
    $(this).removeClass("hover");
  });

  $.getJSON("/rest/game/" + year, function(data) {
    if (data["success"]) {
       game = data["game"]
       afc_team = game["afc_team"]
       if (typeof afc_team == 'string') {
           $("#afc-label").text(afc_team);
       }
       nfc_team = game["nfc_team"]
       if (typeof nfc_team == 'string') {
           $("#nfc-label").text(nfc_team);
       }
       afc_values = game["afc_values"];
       if (afc_values !== null && afc_values.length == 10) {
           for (i = 0; i < 10; i++) {
               val = afc_values[i]
               $("[data-afc='" + i + "']").html(val);
           }
       }

       nfc_values = game["nfc_values"];
       if (nfc_values !== null && nfc_values.length == 10) {
           for (i = 0; i < 10; i++) {
               val = nfc_values[i]
               $("[data-nfc='" + i + "']").html(val);
           }
       }
       for (i = 0; i < game["squares"].length; i++) {
           n = game["squares"][i]["name"];
           if (typeof n == 'string' && n.length > 0) {
               $("[data-square-pos='" + i + "'").html(n);
           }
       }
    }
  }).fail(function(xhr){
    console.log("Failed to load data from server");
  });
  
});
