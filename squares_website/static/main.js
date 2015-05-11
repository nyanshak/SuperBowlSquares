

$(function() {

  var game_id = $('input:hidden[name=game_id]').val();

  $(".td-noname, .td-named, .td-verified").hover(function(){
    $(this).addClass("hover");
  }, function(){
    $(this).removeClass("hover");
  });

  $.getJSON("/rest/game/" + game_id, function(data) {
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
               square = $("[data-square-pos='" + i + "'");
               square.text(n);
               if (game["squares"][i]["verified"]) {
                   square.addClass("td-verified").removeClass("td-noname");
               } else {
                   square.addClass("td-named").removeClass("td-noname");
               }
           }
       }
       $("#game-name").text(game["game_name"]).css("text-align", "center");
    }
  }).fail(function(xhr){
    console.log("Failed to load data from server");
  });
  
});
