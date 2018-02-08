function initMap() {
    var mapProp= {
        center:new google.maps.LatLng(51.508742,-0.120850),
        zoom:11,
        mapTypeId:google.maps.MapTypeId.HYBRID
    };
    map=new google.maps.Map(document.getElementById("Map"),mapProp);

    infoWindow = new google.maps.InfoWindow;

    // Try HTML5 geolocation.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(pos);
            map.setZoom(11);
            }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
            });
    } else {
        // Browser doesn't support Geolocation
        handleLocationError(false, infoWindow, map.getCenter());
    }

    map.addListener('bounds_changed', function() {
        document.getElementById('mapbounds').value = map.getBounds();
    });
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}







$(document).ready(function () {

    $('#mapbounds').val(map.getBounds());

    $("form") .submit(function(){
        if ( $("#added").children().length === 0) {
            alert("Du må legge til minst en bruker !");
            return false;
        } else {
            return true;
        }
    });


    function addingFunction(element) {
        username = $(element).parent().text();
        type = $(element).parent().parent().prop('type');

        newelement = "<li class='list-group-item'>"+username+"<span class='badge'><i class='fa fa-minus'></i></span> " +
            "<input name='users' value='"+username+"' type='hidden' class='form-control'> " +
            "</li>";

        switch (type) {
            case 'add':
                var exist = $("#added li:contains("+username+")");
                if (exist.text() === "") {
                    $('#added').append(newelement);
                    $('span').off('click');
                    $('span').on('click', function(e) {
                        addingFunction(this);
                    });
                } else {
                    alert("Brukeren er allerede lagt til !")
                }
                break;
                case 'remove':
                    $("#added li:contains("+username+")").remove();
                    break;
        }
    }

    $('span').on('click', function () {
        addingFunction(this);
    });

    $('#searchUsersButton').on('click', function (e) {
        alert("clikced;");
        var username = $('#searchUsers').val();

        $.post("/searchUsers",
            {
                username: username,
            },
            function(data,status){
            if (status === "success") {
                var results = JSON.parse(data);
                $('#registered').empty();
                for (var i = 0; i < results.length; i++) {
                    var newelement = "<li class='list-group-item'>"+results[i]+"<span class='badge'><i class='fa fa-plus'></i></span></li>";
                    $('#registered').append(newelement);
                }
                $('span').off('click');
                $('span').on('click', function(e) {
                    addingFunction(this);
                });
            } else {
                alert("Database Connection failure");
            }
        });
    });

    var dateToday = new Date();
    var dates = $("#date") .datepicker({
        defaultDate: "+3m",
        changeMonth: true,
        numberOfMonths: 1,
        minDate: dateToday,
        onSelect: function(selectedDate) {
            var option = this.id == "from" ? "minDate" : "maxDate",
                instance = $(this).data("datepicker").css({"position": "relative", "z-index": 999999});
            date = $.datepicker.parseDate(instance.settings.dateFormat || $.datepicker._defaults.dateFormat, selectedDate, instance.settings);
            dates.not(this).datepicker("option", option, date);
        }
    });
});