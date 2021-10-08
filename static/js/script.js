$(window).on('load', function() {
    $('#staticBackdrop').appendTo("body").modal('show');
})

$("#filter5").hover(function(){
    $("#filter5").css("color", "gold");
    $("#filter4").css("color", "gold");
    $("#filter3").css("color", "gold");
    $("#filter2").css("color", "gold");
    $("#filter1").css("color", "gold");
    }, function(){
        $("#filter5").css("color", "grey");
        $("#filter4").css("color", "grey");
        $("#filter3").css("color", "grey");
        $("#filter2").css("color", "grey");
        $("#filter1").css("color", "grey");
  });

  $("#filter4").hover(function(){
    $("#filter4").css("color", "gold");
    $("#filter3").css("color", "gold");
    $("#filter2").css("color", "gold");
    $("#filter1").css("color", "gold");
    }, function(){
       
        $("#filter4").css("color", "grey");
        $("#filter3").css("color", "grey");
        $("#filter2").css("color", "grey");
        $("#filter1").css("color", "grey");
  });
  $("#filter3").hover(function(){
    $("#filter3").css("color", "gold");
    $("#filter2").css("color", "gold");
    $("#filter1").css("color", "gold");
    }, function(){
        $("#filter3").css("color", "grey");
        $("#filter2").css("color", "grey");
        $("#filter1").css("color", "grey");
  });
  $("#filter2").hover(function(){
    $("#filter2").css("color", "gold");
    $("#filter1").css("color", "gold");
    }, function(){
        $("#filter2").css("color", "grey");
        $("#filter1").css("color", "grey");
  });
  $("#filter1").hover(function(){
    $("#filter1").css("color", "gold");
    }, function(){
        $("#filter1").css("color", "grey");
  });