var choice_panel_toggled;
function auto_adjust_dimentions() {
            window_width = $(window).width();
            if (window_width > 800) {
                    $("#Map").css({"width":"70%","display":"inline-block"});
                    $("#ChoicePanel").css({"width":"30%","display":"inline-block"});
                    $("#pac-card").css("width","90%");
                    $("#show_map_btn").css("display","none");
                    choice_panel_toggled = false;
                }
            else {
                    $("#Map").css({"width":"100%","display":"inline-block"});
                    $("#ChoicePanel").css("width","100%");
                    $("#ChoicePanel").hide();
                    $("#pac-card").css("width","80%");
                    $("#show_map_btn").css({"width":"100%","display":"inline"});
                    choice_panel_toggled = true;
                }
        }

        $(document).ready(function () {

            $("#info_window").hide();

            // trigger for varying the lines/path width
            $("input[name~='Weight']").change(function (e) {
                for (var key in current_shapes) {
                    if (current_shapes[key]['type'] == "ROAD") {
                        shape = current_shapes[key]['shape'];
                        shape.setMap(null);
                        shape.strokeWeight = $("input[name~='Weight']").val();
                        shape.setMap(map);
                    }
                }
            });

            // trigger for varying the area opacity
            $("input[name~='Opacity']").change(function (e) {
                for (var key in current_shapes) {
                    if (current_shapes[key]['type'] == "AREA") {
                        shape = current_shapes[key]['shape'];
                        shape.setMap(null);
                        shape.strokeOpacity = ($("input[name~='Opacity']").val()/10);
                        shape.fillOpacity = ($("input[name~='Opacity']").val()/10);
                        shape.setMap(map);
                    }
                }

            });

            // code for adjusting dimentions on big and small screen devices
            auto_adjust_dimentions();
            $(window).resize(function () {
                auto_adjust_dimentions();
            });
            $("#toggle_panel").click(function () {

                window_width = $(window).width();
                if (window_width > 800) {
                    if(choice_panel_toggled) {
                        $("#Map").css({"width":"70%","display":"inline-block"});
                        $("#ChoicePanel").toggle();
                    } else {
                        $("#Map").css({"width":"100%","display":"inline-block"});
                        $("#ChoicePanel").toggle();
                    }
                } else {
                    $("#ChoicePanel").toggle();
                    $("#Map").toggle();
                }

                if(choice_panel_toggled) {
                    choice_panel_toggled = false;
                } else {
                    choice_panel_toggled = true;
                }


            });
            $("#show_map_btn").click(function () {
                auto_adjust_dimentions();
            });

            $("#filter_interviewers").chosen({
                width:'100%',
                placeholder_text_multiple: "Alle Interviewere"
            });

            $("#clustring_switch").change(function () {

                if ($("#clustring_switch").is(":checked") == true) {

                    var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
                    markers = [];

                    for (var key in current_shapes) {
                        if (current_shapes[key]["type"] == "POINT") {
                            markers.push(current_shapes[key]["marker"]);
                        }
                    }

                    // Add a marker clusterer to manage the markers.
                    markerCluster = new MarkerClusterer(map, markers,
                        {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
                        });

                } else {
                    // kode to remove marker clustring
                    for (var i=0;i<markers.length;i++) {
                        markerCluster.removeMarker(markers[i]);
                    }

                    for (var key in current_shapes){
                        current_shapes[key]["marker"].setMap(map);
                        if (current_shapes[key]["type"] == "AREA" || current_shapes[key]["type"] == "ROAD") {
                           current_shapes[key]["shape"].setMap(map);
                       }
                    }

                }
            });

        });