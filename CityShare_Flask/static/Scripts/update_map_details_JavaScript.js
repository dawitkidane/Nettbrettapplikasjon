    $(document).ready(function () {


        $('#AddQuestionButton').on('click', function () {
           added_questions = $("#category_body_questions").children().text();
           current_question = $("#Question").val();

           if (added_questions.includes(current_question) || current_question == "") {
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
               $('#Question').empty();
               $('#'+question_ID+'').off('click');
               $('#'+question_ID+'').on('click', function(e) {
                   $(this).parent().remove();
               });
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
                                $('#searchInterviewers').empty();
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
                                $('#searchAdministrators').empty();
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

        $('#AddInterviewersButton').hide();
        $('#AddAdministratorsButton').hide();

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

        // Checking that users are added to the map before submitting

        $("#form").submit(function(){
            if ( $("#category_body_Interviewers").children().length === 0) {
                alert("Du må legge til minst en Interviewer !");
                return false;
            }
            if ($("#category_body_questions").children().length === 0) {
                alert("Du må legge til minst et spørsmål !");
                return false;
            }
            if ($("#category_body_Administrators").children().length === 0) {
                alert("Du må legge til minst en Administrator !");
                return false;
            }
            return true;

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


        $("#colorpicker_road").spectrum({
            color: "#3355cc"
        });
        $("#colorpicker_area").spectrum({
            color: "#3355cc"
        });
    });