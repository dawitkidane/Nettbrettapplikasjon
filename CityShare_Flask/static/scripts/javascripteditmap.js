function initMap() {
    var mapOptions = {
        center: new google.maps.LatLng(51.5, -0.12),
        zoom: 10,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        gestureHandling: 'none',
        zoomControl: false,
        fullscreenControl: false
    }
    map = new google.maps.Map(document.getElementById("Map"), mapOptions);
}
