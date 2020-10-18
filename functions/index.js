// Jackson Meade | HackNC 2020 Firebase Functions
// Sunday, October 18th, 6:38AM, about 1800mg of caffeine in

//IMPORTS
import { database } from "firebase-admin";
import Geocode from "react-geocode";


//BOILERPLATE
const functions = require('firebase-functions');

const admin = require('firebase-admin')

const db = admin.database();

// As soon as an order is created, find live users that can fulfill the request by geolocation
exports.order_matchUsers = db.ref('/orders/{orderID}').onCreate((snapshot, context) => {
  // Grab current value of what was written to realtime DB (See docs for boilerplate)
  const original = snapshot.val();

  const donor = (db.ref('users/' + original.participants.u_donor));
  // Find a distributor, static or not
  var distributor = Find_A_Distributor(donor.address1 + " " + donor.address2, !donor.static);
  original.participants.u_dist = distributor;
  // Now call the app to map:

  // Must return a Promise when performing async tasks
  return snapshot.ref.parent.child();
});


// We cannot guarantee a return on the creation of an order, so as soon as someone goes online, let's find orders to match
exports.user_matchOrders = db.ref('/users/{userID}/static').onUpdate((change, context) => {
  const before = change.before.val();
  const after = change.after.val();

  // Safety feature to prevent runaway if self-called
  if (before.val() === after.val()) {
    console.log("No User Update")
    return null;
  }
  const aRef = change.after.ref;
  const usertype = aRef.child('account_type');

  // We NEVER create direct connections between donors and customers for security. If they are of this type, find a 
  //   mobile or static distributor to either deliver or send them to.
  if (usertype == "customer" || usertype == "donor") {
    // A distributor always has the opposite static value to its serviced customer or donor
    var distributor = Find_A_Distributor((aRef.child('address1') + ' ' + aRef.child(address2)), !(aRef.child('static')));

    // Now we run the superficial logic to instruct users

  }
  else if (usertype == "distributor") {

  }
  else {
    console.log("Invalid user type inputted.")
  }

  return null;
});

//A WAY TO IMPROVE: Make this function sensitive to the distributor's location so that we can prioritize.
function Find_A_Distributor(location, distributorType) {
  Geocode.setApiKey('AIzaSyC9-ztW_ZL8MZ_YMln6wxWouS09Ad8qb2Y');

  Geocode.setLanguage("en");

  // LATER UPDATE POTENTIAL: Localize this part of the code based on the "Community" location
  Geocode.setRegion("us");

  Geocode.fromAddress(location).then(
    response => {
      const { _lat, _lng } = response.results[0].geometry.location;

      // Now that we know we have an address, get a distributor in range
      admin.auth().listUsers().then((userRecords) => {
        // Set up dictionary for distributors and their distances
        // Why do we want a whole list? Well, for later functionality, if we wanted to list
        //   all the distributors in an area, or add functionality that lets people prioritize their
        //   distributor (we want to encourage trusting, built-up relationships), this will give us
        //   the freedom to do so.

        // Actually, initialize this value at the max distance allowed.
        var distance_min = 1e9;
        // Create a dictionary of users associated with their distance from the request
        var dist_list = {}

        // Iterate through users...
        userRecords.users.forEach((user) => {
          // ...and if it's a distributor, add it to the list with a distance given
          // Also, make sure that we've specified whether we want static or mobile distribution
          if (user.account_type == "distributor" && user.static == distributorType) {
            Geocode.fromAddress(user.address1 + " " + user.address2).then((userLoc) => {
              const { lat, lng } = response.results[0].geometry.location;

              const calc_distance = haversine({ _lat, _lng }, { lat, lng });
              if (calc_distance < distance_min) {
                distance_min = calc_distance
              }
              dist_list[calc_distance] = user;

            }).catch((error) => console.log(error));
          }
        });

        // Now that we have a close distributor, let's pair them up
        return dist_list[distance_min];
      }).catch((error) => console.log(error));

    },
    error => {
      console.error(error);
    }
  );

}

function haversine({ lat_source, lng_source }, { lat_dest, lng_dest }) {
  // Source/credit: http://www.movable-type.co.uk/scripts/latlong.html
  const R = 6371e3; // metres
  const φ1 = lat_source * Math.PI / 180; // φ, λ in radians
  const φ2 = lat_dest * Math.PI / 180;
  const Δφ = (lat_dest - lat_source) * Math.PI / 180;
  const Δλ = (lng_dest - lng_source) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) *
    Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const d = R * c; // in metres

  return d / 1000 // in kilometres
}