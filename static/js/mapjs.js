console.info('spa_directions.js loaded');

/* code for simple map */
const directionsInfo = document.querySelector('#directions-info');
const directionsButton = document.querySelector('#get-directions');
directionsButton.addEventListener('click', getLocation);
let directionsService;
let directionsDisplay;

//Get's your current location
function getLocation(){
  navigator.geolocation.getCurrentPosition(function(position) {
    directionsInfo.innerHTML = `You appear to be at: ${position.coords.latitude}, ${position.coords.longitude}`;
    var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    initMap(pos);
  });
}

//Creates the map
function initMap(location){
  directionsMap = new google.maps.Map(document.querySelector('#directions-map'), {
    center: location,
    zoom: 16
  });

  directionsService = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer();
  directionsDisplay.setMap(directionsMap);
  let destination = new google.maps.LatLng(41.8781, 87.6298); //replace these with actual destination

  calcRoute(location, destination);

}

//Calculates the route
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
        label: 'destination'
      });
    }
  })
}