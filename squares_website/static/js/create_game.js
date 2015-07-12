$(function(){
    $("#gameBtn").click(function(evt) {
        evt.preventDefault()
        $.ajax({
            url: '/rest/game/create',
            type: 'POST',
            data: JSON.stringify({name: $("#gameName").val(), token: $("#gameToken").val()}),
            contentType: "application/json",
            success: function(data) {
                gameId = data['game']['game_id']
                console.log(data)
                BootstrapDialog.show({
                    title: 'Success',
                    message: 'Your game was created successfully',
                    closable: false,
                    buttons: [{
                        id: 'btn-ok',
                        icon: 'glyphicon glyphicon-check',
                        label: 'OK',
                        cssClass: 'btn-primary',
                        autospin: 'false',
                        action: function() {
                            window.location.href = '/game/' + gameId
                        }
                    }]
                })
            },
            error: function(xhr, ajaxOptions, thrownError) {
                e = "You must provide a password"
                BootstrapDialog.show({
                    title: 'Error',
                    message: e,
                    buttons: [{
                        id: 'btn-error',
                        icon: 'glyphicon glyphicon-ban-circle',
                        label: 'OK',
                        cssClass: 'btn-primary',
                        autospin: 'false',
                        action: function(me) {
                            me.close()
                        }
                    }]
                })
            }
        })
    })
})
