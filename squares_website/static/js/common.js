function prepBoard(){

  var gameId = $('input:hidden[name=gameId]').val()

  $(".td-noname, .td-named, .td-verified").hover(function(){
    $(this).addClass("hover")
  }, function(){
    $(this).removeClass("hover")
  })

  $.getJSON("/api/game/" + gameId, function(data) {
    if (data["success"]) {
       game = data["game"]
       afc_team = game["afc_team"]
       if (typeof afc_team == 'string') {
           $("#afc-label").text(afc_team)
       }
       nfc_team = game["nfc_team"]
       if (typeof nfc_team == 'string') {
           $("#nfc-label").text(nfc_team)
       }
       afc_values = game["afc_values"]
       if (afc_values !== null && afc_values.length == 10) {
           for (i = 0; i < 10; i++) {
               val = afc_values[i]
               $("[data-afc='" + i + "']").html(val)
           }
       }

       nfc_values = game["nfc_values"]
       if (nfc_values !== null && nfc_values.length == 10) {
           for (i = 0; i < 10; i++) {
               val = nfc_values[i]
               $("[data-nfc='" + i + "']").html(val)
           }
       }
       for (i = 0; i < game["squares"].length; i++) {
           n = game["squares"][i]["name"]
           if (typeof n == 'string' && n.length > 0) {
               square = $("[data-square-pos='" + i + "'")
               square.text(n)
               if (game["squares"][i]["verified"]) {
                   square.addClass("td-verified").removeClass("td-noname")
               } else {
                   square.addClass("td-named").removeClass("td-noname")
               }
           }
       }
       $("#game_name").html(game["game_name"]).css('text-align', 'center')
    }
    $("#game-div").show()
  }).fail(function(xhr){
    url = 'create'
    window.setTimeout(function(){ window.location.href = url }, 5000)
    $("#middle").html('<h1>Error</h1><p>That game does not exist. Click <a href="' + url + '">here</a> to make a new game.')
    $("#game-div").show()
  })
  
}
