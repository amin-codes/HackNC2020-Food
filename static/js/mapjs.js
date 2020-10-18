console.info('script.js loaded');

/* code for simple map */
const directionsInfo = document.querySelector('#directions-info');
const directionsButton = document.querySelector('#get-directions');
directionsButton.addEventListener('click', getLocation);
let directionsService;
let directionsDisplay;

function getLocation(){

  navigator.geolocation.getCurrentPosition(function(position) {
    directionsInfo.innerHTML = `You appear to be at: ${position.coords.latitude}, ${position.coords.longitude}`;
    var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    initMap(pos);
  });
}
function initMap(){
  directionsMap = new google.maps.Map(document.querySelector('#directions-map'), {
    center: {lat:35.1252965, lng:-80.7911135},
    zoom: 16
  });

  directionsService = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer();
  directionsDisplay.setMap(directionsMap);
  let destination = new google.maps.LatLng(47.6795273,-70.8697928);

  calcRoute({lat:35.1252965, lng:-80.7911135}, destination);

}

function calcRoute(start, destination){
  let request = {
    origin: start,
    destination: destination,
    travelMode: google.maps.TravelMode.DRIVING //
  };
  directionsService.route(request, function(response, status){
    if(status == 'OK'){
      directionsDisplay.setDirections(response);
      let starter = new google.maps.Marker({
        position: start,
        map: directionsMap,
        label: 'you are here'
      });
      let marker = new google.maps.Marker({
        position: destination,
        map: directionsMap,
        label: 'Destination'
      });
    }

  })
}