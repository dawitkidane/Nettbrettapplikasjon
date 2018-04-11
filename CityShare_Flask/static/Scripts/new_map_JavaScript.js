function getBoundsZoomLevel(bounds, mapDim) {
    var WORLD_DIM = { height: 256, width: 256 };
    var ZOOM_MAX = 21;

    function latRad(lat) {
        var sin = Math.sin(lat * Math.PI / 180);
        var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
        return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
    }


    function zoom(mapPx, worldPx, fraction) {
        return Math.floor(Math.log(mapPx / worldPx / fraction) / Math.LN2);
    }

    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();

    var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;

    var lngDiff = ne.lng() - sw.lng();
    var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

    var latZoom = zoom(mapDim.height, WORLD_DIM.height, latFraction);
    var lngZoom = zoom(mapDim.width, WORLD_DIM.width, lngFraction);

    return Math.min(latZoom, lngZoom, ZOOM_MAX);
}

var map = null;
function initMap() {
    map = new google.maps.Map(document.getElementById('Map'), {
        zoom: 11,
        center: {lat: 58.969975, lng: 5.733107},
        mapTypeControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
        streetViewControlOptions: {
            position: google.maps.ControlPosition.RIGHT_CENTER
        },
        zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_CENTER
        },
        fullscreenControl: false
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(pos);
            map.setZoom(11);
            }, function() {
            // bruker ønsker ikke å dele sin posisjon
        });
    } else {
        // Browser doesn't support Geolocation
        alert("Din browser støtter ikke geografisk gjenfinning");
    }

    var bounds = {
        north: 0,
        south: 0,
        east: 0,
        west: 0
    };
    var rectangle = new google.maps.Rectangle({
        bounds: bounds,
        editable: true,
        draggable: true
    });

    map.addListener('bounds_changed', function() {
        if (map.getZoom() < 3) map.setZoom(3);

        lat_center = map.getCenter().lat();
        lng_center = map.getCenter().lng();
        n = (map.getBounds().getNorthEast().lat()+lat_center)/2;
        s = (map.getBounds().getSouthWest().lat()+lat_center)/2;
        e = (map.getBounds().getNorthEast().lng()+lng_center)/2;
        w = (map.getBounds().getSouthWest().lng()+lng_center)/2;
        bounds = {
            north: n,
            south: s,
            east: e,
            west: w
        };
        rectangle.setMap(null);
        rectangle.setBounds(bounds);
        rectangle.setMap(map);
        });

    rectangle.addListener('bounds_changed', function () {
        $('#geo_boundery').val(rectangle.getBounds());

        var $mapDiv = $('#Map');
        var mapDim = { height: $mapDiv.height(), width: $mapDiv.width() };
        calculated_zoom = getBoundsZoomLevel(rectangle.getBounds(), mapDim);
        $('#geo_zoom').val(calculated_zoom+1);
        });




    var card = document.getElementById('pac-card');
    var input = document.getElementById('pac-input');
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(card);

    var autocomplete = new google.maps.places.Autocomplete(input);

    // Bind the map's bounds (viewport) property to the autocomplete object,
    // so that the autocomplete requests use the current map bounds for the
    // bounds option in the request.
    autocomplete.bindTo('bounds', map);

    autocomplete.addListener('place_changed', function() {

        var place = autocomplete.getPlace();
        if (!place.geometry) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);  // Why 17? Because it looks good.
        }

        var address = '';
        if (place.address_components) {
            address = [
                (place.address_components[0] && place.address_components[0].short_name || ''),
                (place.address_components[1] && place.address_components[1].short_name || ''),
                (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');
        }


        });
    }

    $(document).ready(function () {

        $('#AddInterviewersButton').hide();
        $('#AddAdministratorsButton').hide();

        // Checking that users are added to the map before submitting
        $("#form").submit(function (e) {
            var missing_values = true;
            alert_msg = "Manglende Input Verdier: \nDu må legge til minst en av følgende";

            if ($("#category_body_point").children().length === 0) {
                alert_msg += "\n -> Punkt Kategorier !";
                missing_values = false;
                $("#add_points_btn").removeClass("btn-info");
                $("#add_points_btn").addClass("btn-danger");
            } else {
                $("#add_points_btn").removeClass("btn-danger");
                $("#add_points_btn").addClass("btn-info");
            }

            if ($("#category_body_Road").children().length === 0) {
                alert_msg += "\n -> Vei Kategorier !";
                missing_values = false;
                $("#add_roads_btn").removeClass("btn-info");
                $("#add_roads_btn").addClass("btn-danger");
            } else {
                $("#add_roads_btn").removeClass("btn-danger");
                $("#add_roads_btn").addClass("btn-info");
            }

            if ($("#category_body_area").children().length === 0) {
                alert_msg += "\n -> Område Kategorier !";
                missing_values = false;
                $("#add_areas_btn").removeClass("btn-info");
                $("#add_areas_btn").addClass("btn-danger");
            } else {
                $("#add_areas_btn").removeClass("btn-danger");
                $("#add_areas_btn").addClass("btn-info");
            }

            if ($("#category_body_Interviewers").children().length === 0) {
                alert_msg += "\n -> Interviewer !";
                missing_values = false;
                $("#add_interviewers_btn").removeClass("btn-info");
                $("#add_interviewers_btn").addClass("btn-danger");
            } else {
                $("#add_interviewers_btn").removeClass("btn-danger");
                $("#add_interviewers_btn").addClass("btn-info");
            }

            if ($("#category_body_Administrators").children().length === 0) {
                alert_msg += "\n -> Administratorer !";
                missing_values = false;
                $("#add_administrators_btn").removeClass("btn-info");
                $("#add_administrators_btn").addClass("btn-danger");
            } else {
                $("#add_administrators_btn").removeClass("btn-danger");
                $("#add_administrators_btn").addClass("btn-info");
            }

            if ($("#category_body_questions").children().length === 0) {
                alert_msg += "\n -> Spørsmål !";
                missing_values = false;
                $("#add_questions_btn").removeClass("btn-info");
                $("#add_questions_btn").addClass("btn-danger");
            } else {
                $("#add_questions_btn").removeClass("btn-danger");
                $("#add_questions_btn").addClass("btn-info");
            }

            if (!missing_values) {
                alert(alert_msg);
            }
            return missing_values;
        });

        // Method to add Point categories
        $("#add_point_category").on('click', function () {
            var icon_name = $('#point_name').val();
            var icon_type = "Point";
            var icon_img = $( "#point_icon option:selected" ).val();
            var icon = "<img src='../static/icons/"+icon_img+"'>";

            var text = icon+" <strong>Name</strong>: "+icon_name+", <strong>Type</strong>: "+icon_type;
            var value = icon_name+","+icon_type+","+icon_img;

            var new_category = "<li class='list-group-item'>"+text
                +"<span class='badge delete_cat'>"
                +"<i class='fa fa-minus'></i>"
                +"</span>"
                +"<input name='point_categories' value='"+value+"' type='hidden' class='form-control'>" +
                "</li>";

            var brukt = false;
            $("#category_body_point :input[name~='point_categories']").each(function(){
                var string_elements = $(this).val().split(",");
                var compared_elements = value.split(",");
                if(string_elements[0] == compared_elements[0] || string_elements[2] == compared_elements[2]) {
                    brukt = true;
                    return;
                }
            });

            if (icon_name != "" && brukt != true) {
                var list = $('#category_body_point');
                list.append(new_category);
                $('#point_name').val("");

                $('.delete_cat').off();
                $('.delete_cat').on('click', function () {
                    $(this).parent().remove();
                });
            } else if (brukt == true) {
                alert("dette ikonet og/eller kategorinavnet er allerede brukt");
            } else {
                alert("Fyll ut alle felter");
            }
        });

        // Method to add Road categories
        $("#add_road_category").on('click', function () {
            var icon_name = $('#road_name').val();
            var icon_type = "Road";
            //var road_color = $( "#road_color input" ).val();
            var road_color = "#"+$("#colorpicker_road").spectrum("get").toHex();
            var color_div = "<div style='background-color:"+road_color+"; width: 30px; height: 30px'></div>";

            var text = color_div+" <strong>Name</strong>: "+icon_name+", <strong>Type</strong>: "+icon_type;
            var value = icon_name+","+icon_type+","+road_color;

            var new_category = "<li class='list-group-item'>"+text
                +"<span class='badge delete_cat'>"
                +"<i class='fa fa-minus'></i>"
                +"</span>"
                +"<input name='road_categories' value='"+value+"' type='hidden' class='form-control'>" +
                "</li>";

            var brukt = false;
            $("#category_body_Road :input[name~='road_categories']").each(function(){
                var string_elements = $(this).val().split(",");
                var compared_elements = value.split(",");
                if(string_elements[0] == compared_elements[0] || string_elements[2] == compared_elements[2]) {
                    brukt = true;
                    return;
                }
            });

            if (icon_name != "" && brukt != true) {
                var list = $('#category_body_Road');
                list.append(new_category);
                $('#road_name').val("");

                $('.delete_cat').off();
                $('.delete_cat').on('click', function () {
                    $(this).parent().remove();
                });
            } else if (brukt == true) {
                alert("denne fargen og/eller kategorinavnet er allerede brukt");
            } else {
                alert("Fyll ut alle felter");
            }
        });

        // Method to add Area categories
        $("#add_area_category").on('click', function () {
            var icon_name = $('#area_name').val();
            var icon_type = "Area";
            //var area_color = $( "#area_color input" ).val();
            var area_color = "#"+$("#colorpicker_area").spectrum("get").toHex();
            var color_div = "<div style='background-color:"+area_color+"; width: 30px; height: 30px'></div>";
            var text = color_div+" <strong>Name</strong>: "+icon_name+", <strong>Type</strong>: "+icon_type;
            var value = icon_name+","+icon_type+","+area_color;

            var new_category = "<li class='list-group-item'>"+text
                +"<span class='badge delete_cat'>"
                +"<i class='fa fa-minus'></i>"
                +"</span>"
                +"<input name='area_categories' value='"+value+"' type='hidden' class='form-control'>" +
                "</li>";

            var brukt = false;
            $("#category_body_area :input[name~='area_categories']").each(function(){
                var string_elements = $(this).val().split(",");
                var compared_elements = value.split(",");
                if(string_elements[0] == compared_elements[0] || string_elements[2] == compared_elements[2]) {
                    brukt = true;
                    return;
                }
            });
            if (icon_name != "" && brukt != true) {
                var list = $('#category_body_area');
                list.append(new_category);
                $('#area_name').val("");

                $('.delete_cat').off();
                $('.delete_cat').on('click', function () {
                    $(this).parent().remove();
                });
            } else if (brukt == true) {
                alert("denne fargen og/eller kategorinavnet er allerede brukt");
            } else {
                alert("Fyll ut alle felter");
            }
        });

        // Adding Interviewers / jQuery
        $('#SearchInterviewersButton').on('click', function (e) {
            var username = $('#searchInterviewers').val();

            if (username != '') {
                $.post("/searchUsers",{ username: username }, function(data,status){
                    if (status === "success") {
                        var results = JSON.parse(data);
                        var user = results[0];

                        if (results.length > 0) {
                            var addedusers = $("#category_body_Interviewers").children().text();
                            if (addedusers.includes(username) || addedusers.includes(user)) return;
                            $('#AddInterviewersButton').show();
                            $('#AddInterviewersButton').off('click');
                            $('#AddInterviewersButton').on('click', function(e) {
                                var newelement = "<li class='list-group-item'>"+user
                                    +"<span id='"+user+"_Interviewer' class='badge'>"
                                    +"<i class='fa fa-minus'></i>"
                                    +"</span>"
                                    +"<input name='Interviewers' value='"+user+"' type='hidden' class='form-control'>"
                                    +"</li>";
                                $('#category_body_Interviewers').append(newelement);
                                $('#AddInterviewersButton').hide();
                                $('#searchInterviewers').val("");
                                $('#'+user+'_Interviewer').off('click');
                                    $('#'+user+'_Interviewer').on('click', function(e) {
                                        $(this).parent().remove();
                                    });
                                });
                        }

                    } else {
                        alert("Database Connection failure");
                    }
                });
            }
        });

        // Adding Administrators / jQuery
        $('#SearchAdministratorsButton').on('click', function (e) {
            var username = $('#searchAdministrators').val();

            if (username != '') {
                $.post("/searchUsers",{ username: username }, function(data,status){
                    if (status === "success") {
                        var results = JSON.parse(data);
                        var user = results[0];

                        if (results.length > 0) {
                            var addedusers = $("#category_body_Administrators").children().text();
                            if (addedusers.includes(username) || addedusers.includes(user)) return;
                            $('#AddAdministratorsButton').show();
                            $('#AddAdministratorsButton').off('click');
                            $('#AddAdministratorsButton').on('click', function(e) {
                                var newelement = "<li class='list-group-item'>"+user
                                    +"<span id='"+user+"_Admin' class='badge'>"
                                    +"<i class='fa fa-minus'></i>"
                                    +"</span>"
                                    +"<input name='Administrators' value='"+user+"' type='hidden' class='form-control'>"
                                    +"</li>";
                                $('#category_body_Administrators').append(newelement);
                                $('#AddAdministratorsButton').hide();
                                $('#searchAdministrators').val("");
                                $('#'+user+'_Admin').off('click');
                                    $('#'+user+'_Admin').on('click', function(e) {
                                        $(this).parent().remove();
                                    });
                                });
                        }

                    } else {
                        alert("Database Connection failure");
                    }
                });
            }
        });

        // Adding Questions
        $('#AddQuestionButton').on('click', function () {
           added_questions = $("#category_body_questions").children().text();
           current_question = $("#Question").val();

           if (current_question == "") {
               alert("Du må skrive et spørsmål !");
               return;
           } else if (added_questions.includes(current_question)) {
               alert("Dette spørsmålet er allerede lagt til.");
               return;
           } else {
               question_ID = current_question.replace(/ /g, "_");
               var newelement = "<li class='list-group-item'>"+current_question
                                    +"<span id='"+question_ID+"' class='badge'>"
                                    +"<i class='fa fa-minus'></i>"
                                    +"</span>"
                                    +"<input name='questions' value='"+current_question+"' type='hidden' class='form-control'>"
                                    +"</li>";
               $('#category_body_questions').append(newelement);
               $('#Question').val("");

               $('#'+question_ID+'').off('click');
               $('#'+question_ID+'').on('click', function(e) {
                   $(this).parent().remove();
               });
           }
        });

        // Datepicker - jQuery
        var dateToday = new Date();
        var dates = $("#date").datepicker({
            defaultDate: "+3m",
            changeMonth: true,
            numberOfMonths: 1,
            minDate: dateToday,
            onSelect: function(selectedDate) {
                var option = this.id == "from" ? "minDate" : "maxDate",
                    instance = $(this).data("datepicker")//.css({"position": "relative", "z-index": 999999});
                date = $.datepicker.parseDate(instance.settings.dateFormat || $.datepicker._defaults.dateFormat, selectedDate, instance.settings);
                dates.not(this).datepicker("option", option, date);
                $(this).blur();
            }
        });

        // code for adjusting dimentions on big and small screen devices
        var choice_panel_toggled;
        function auto_adjust_dimentions() {
            window_width = $(window).width();
            if (window_width > 800) {
                $("#Map").css({"width":"70%","display":"inline-block"});
                $("#ChoicePanel").css({"width":"30%","display":"inline-block"});
                $("#pac-card").css("width","90%");
                $(".btn-success, .btn-danger").css({"width":"49%","display":"inline"});
                $("#show_map_btn").css("display","none");
                choice_panel_toggled = false;
            } else {
                $("#Map").css({"width":"100%","display":"inline-block"});
                $("#ChoicePanel").css("width","100%");
                $("#ChoicePanel").hide();
                $("#pac-card").css("width","80%");
                $(".btn-success, .btn-danger, #show_map_btn").css({"width":"32%","display":"inline"});
                choice_panel_toggled = true;
            }
        }
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

        $("#colorpicker_road").spectrum({
            color: "#3355cc"
        });
        $("#colorpicker_area").spectrum({
            color: "#3355cc"
        });
    });