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

            // function to listen to the category type changing by the user,
            // and add the neccessary eventlistners to the map
            $("input[name~='New_Marker']").change(function (e) {
                var changed_to = $(this).val();
                var icon = $(this).siblings('img').attr('src'); // only used by shapes with type points
                var category_id = $(this).attr('id');

                if (changed_to == "Area" || changed_to == "Road") {
                    icon = "../static/Images/edit.png";
                    map.setOptions({ draggableCursor : "url("+icon+") 20 50, default" });
                    color = $(this).siblings('div').css('background-color');
                    var draw_mode = false;
                    var points_array = [];
                    var line = null;
                }

                clear_map_events();

                switch(changed_to) {

                    // case current mode is Point
                    case "Point":

                        map.setOptions({ draggableCursor : "url("+icon+") 20 50, default" });

                        var clicklistener = google.maps.event.addListener(map,'click',function(event) {

                            handle_on_close_info_window();

                            if (event.latLng.lat() < southwestcorner.lat() && event.latLng.lat() > northeastcorner.lat()
                            && event.latLng.lng() < southwestcorner.lng() && event.latLng.lng() > northeastcorner.lng()) {

                                var marker = new google.maps.Marker({
                                    position: event.latLng,
                                    icon: icon,
                                    animation: google.maps.Animation.DROP
                                });
                                var content_window = $('#info_window').html();
                                var infowindow = new google.maps.InfoWindow({
                                    content: content_window
                                });

                                var new_point = {
                                    "type": "POINT",
                                    "marker": marker,
                                    "infowindow": infowindow,
                                    "category_ID": category_id,
                                    "center": marker.getPosition().toString(),
                                    "area_or_path": "",
                                    "title": "",
                                    "description": "",
                                    "rating": $("input[name~='rating']").val()
                                };

                                register_shape(new_point);


                                google.maps.event.addListener(marker, 'click', function (event) {
                                    handle_marker_click(infowindow, marker);
                                });

                                google.maps.event.addListener(infowindow, 'closeclick', function () {
                                    handle_outside_bounds_click();
                                    handle_on_close_info_window();
                                });

                                google.maps.event.addListener(infowindow, 'domready', function () {
                                    $("input[name~='title'], textarea[name~='description'], input[name~='rating']").off('blur change');
                                    $("input[name~='title'], textarea[name~='description'], input[name~='rating']").on('blur change', function () {
                                        for (var key in shapes) {
                                            if (shapes[key]["marker"] == marker) {
                                                shapes[key]['title'] = $("input[name~='title']").val();
                                                shapes[key]['description'] = $("textarea[name~='description']").val();
                                                shapes[key]['rating'] = $("input[name~='rating']").val();
                                            }
                                        }
                                    });

                                    $("#delete_btn").off('click');
                                    $("#delete_btn").on('click', function() {
                                        for (var key in shapes) {
                                            if (shapes[key]["marker"] == marker) {
                                                delete_shape(key);
                                            }
                                        }
                                    });
                                });

                            } else {
                                handle_outside_bounds_click();
                            }


                        });

                        listeners.push(clicklistener);

                        break;

                    // case current mode is Road
                    case "Road":

                        click_listener = google.maps.event.addListener(map,'click',function(event) {

                                handle_on_close_info_window();

                                cursor = new google.maps.Marker({
                                    position: event.latLng,
                                    icon: "../static/Images/edit.png",
                                    draggable: true
                                });
                                cursor.setMap(map);
                                map.setOptions({ draggableCursor : undefined});

                                if (draw_mode == false) {
                                    draw_mode = true;

                                    drag_listener = google.maps.event.addListener(cursor,'drag',function(event) {
                                        if (event.latLng.lat() < southwestcorner.lat() && event.latLng.lat() > northeastcorner.lat()
                                            && event.latLng.lng() < southwestcorner.lng() && event.latLng.lng() > northeastcorner.lng()) {
                                            var new_location = event.latLng;
                                            points_array.push(new_location);

                                            if (line != null) line.setMap(null);
                                            var Road = new google.maps.Polyline({
                                                path: points_array,
                                                strokeColor: color,
                                                strokeOpacity: 1,
                                                strokeWeight: 7
                                            });
                                            line = Road;
                                            line.setMap(map);
                                        }
                                    });

                                    var end = google.maps.event.addListener(cursor,'dragend',function(event) {
                                                var marker = new google.maps.Marker({
                                                    position: points_array[Math.round(points_array.length/2)]
                                                });

                                                var content_window = $('#info_window').html();
                                                var infowindow = new google.maps.InfoWindow({
                                                    content: content_window
                                                });

                                                new_road = {
                                                            "marker": marker,
                                                            "type": "ROAD",
                                                            "infowindow": infowindow,
                                                            "center": (points_array[Math.round(points_array.length/2)]).toString(),
                                                            "title": "",
                                                            "description": "",
                                                            "rating": "2",
                                                            "category_ID": (category_id).toString(),
                                                            "area_or_path": makestringfromarray(points_array),
                                                            "points_array": points_array
                                                        };

                                                register_shape(new_road);

                                                line.setMap(null);
                                                points_array = [];

                                                google.maps.event.addListener(marker, 'click', function (event) {
                                                            handle_marker_click(infowindow, marker)
                                                        });

                                                google.maps.event.addListener(infowindow, 'closeclick', function () {
                                                    handle_outside_bounds_click();
                                                    handle_on_close_info_window();
                                                });

                                                google.maps.event.addListener(infowindow, 'domready', function () {
                                                            $("input[name~='title'], textarea[name~='description'], input[name~='rating']").off('blur change');
                                                            $("input[name~='title'], textarea[name~='description'], input[name~='rating']").on('blur change', function () {
                                                                for (var key in shapes) {
                                                                    if (shapes[key]["marker"] == marker) {
                                                                        shapes[key]['title'] = $("input[name~='title']").val();
                                                                        shapes[key]['description'] = $("textarea[name~='description']").val();
                                                                        shapes[key]['rating'] = $("input[name~='rating']").val();
                                                                    }
                                                                }
                                                            });

                                                            $("#delete_btn").off('click');
                                                            $("#delete_btn").on('click', function() {
                                                                for (var key in shapes) {
                                                                    if (shapes[key]["marker"] == marker) {
                                                                        delete_shape(key);
                                                                    }
                                                                }
                                                            });
                                                        });


                                                draw_mode = false;
                                                cursor.setMap(null);
                                            });

                                    listeners.push(end);
                                    listeners.push(drag_listener);

                                }
                            });


                        listeners.push(click_listener);
                        break;

                    // case current mode is Area
                    case "Area":
                        click_listener = google.maps.event.addListener(map,'click',function(event) {

                                handle_on_close_info_window();

                                cursor = new google.maps.Marker({
                                    position: event.latLng,
                                    icon: "../static/Images/edit.png",
                                    draggable: true
                                });
                                cursor.setMap(map);
                                map.setOptions({ draggableCursor : undefined});

                                if (draw_mode == false) {
                                    draw_mode = true;

                                    drag_listener = google.maps.event.addListener(cursor,'drag',function(event) {
                                        if (event.latLng.lat() < southwestcorner.lat() && event.latLng.lat() > northeastcorner.lat()
                                        && event.latLng.lng() < southwestcorner.lng() && event.latLng.lng() > northeastcorner.lng()) {
                                            var new_location = event.latLng;
                                            points_array.push(new_location);

                                            if (line != null) line.setMap(null);
                                            var Road = new google.maps.Polyline({
                                                path: points_array,
                                                strokeColor: color,
                                                strokeOpacity: 1,
                                                strokeWeight: 7
                                            });
                                            line = Road;
                                            line.setMap(map);
                                        }
                                    });

                                    var end = google.maps.event.addListener(cursor,'dragend',function(event) {
                                        var marker = new google.maps.Marker({
                                                    position: computeCentroid(points_array)
                                                });

                                        var content_window = $('#info_window').html();
                                        var infowindow = new google.maps.InfoWindow({
                                                    content: content_window
                                                });

                                        new_road = {
                                                    "marker": marker,
                                                    "type": "AREA",
                                                    "infowindow": infowindow,
                                                    "center": (points_array[Math.round(points_array.length / 2)]).toString(),
                                                    "title": "",
                                                    "description": "",
                                                    "rating": "2",
                                                    "category_ID": (category_id).toString(),
                                                    "area_or_path": makestringfromarray(points_array),
                                                    "points_array": points_array
                                                };

                                        register_shape(new_road);

                                        line.setMap(null);
                                        points_array = [];

                                        google.maps.event.addListener(marker, 'click', function (event) {
                                                    handle_marker_click(infowindow, marker);
                                                });

                                        google.maps.event.addListener(infowindow, 'closeclick', function () {
                                            handle_outside_bounds_click();
                                            handle_on_close_info_window();
                                        });

                                        google.maps.event.addListener(infowindow, 'domready', function () {
                                                    $("input[name~='title'], textarea[name~='description'], input[name~='rating']").off('blur change');
                                                    $("input[name~='title'], textarea[name~='description'], input[name~='rating']").on('blur change', function () {
                                                        for (var key in shapes) {
                                                            if (shapes[key]["marker"] == marker) {
                                                                shapes[key]['title'] = $("input[name~='title']").val();
                                                                shapes[key]['description'] = $("textarea[name~='description']").val();
                                                                shapes[key]['rating'] = $("input[name~='rating']").val();
                                                            }
                                                        }
                                                    });

                                                    $("#delete_btn").off('click');
                                                    $("#delete_btn").on('click', function () {
                                                        for (var key in shapes) {
                                                            if (shapes[key]["marker"] == marker) {
                                                                delete_shape(key);
                                                            }
                                                        }
                                                    });
                                                });


                                        draw_mode = false;
                                        cursor.setMap(null);

                                    });

                                    listeners.push(end);
                                    listeners.push(drag_listener);

                                }

                            });

                        listeners.push(click_listener);

                        break;

                    // a deafult , not realy used. just in case
                    default:
                        break;
                }

            });

            // trigger for varying the lines/path width
            $("input[name~='Weight']").change(function (e) {

                for (var key in shapes) {
                    if (shapes[key]['type'] == "ROAD") {
                        shape = shapes[key]['shape'];
                        shape.setMap(null);
                        shape.strokeWeight = $("input[name~='Weight']").val();
                        shape.setMap(map);
                    }
                }
            });

            // trigger for varying the area opacity
            $("input[name~='Opacity']").change(function (e) {

                for (var key in shapes) {
                    if (shapes[key]['type'] == "AREA") {
                        shape = shapes[key]['shape'];
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

            $("#clustring_switch").change(function () {
                /*
                selected_users = $("#filter_users").val();
                if (selected_users == null) selected_users = [];
                shapes_by_users = get_shapes_by_users(selected_users);
                */

                if ($("#clustring_switch").is(":checked") == true) {

                    var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
                    markers = [];

                    for (var key in shapes) {
                        if (shapes[key]["type"] == "POINT") {
                            markers.push(shapes[key]["marker"]);
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

                    for (var key in shapes){
                        shapes[key]["marker"].setMap(map);
                        if (shapes[key]["type"] == "AREA" || shapes[key]["type"] == "ROAD") {
                           shapes[key]["shape"].setMap(map);
                       }
                    }

                }
            });

        });