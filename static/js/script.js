window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


const btn = document.querySelector('.venue-delete-btn');
if(btn) {
	btn.onclick = function(e) {
		console.log(e);
		const venueID = e.target.dataset['id'];
		fetch('/venues/' + venueID, {
			method: 'DELETE'
		})
		.then(function() {
			window.location = "http://localhost:5000/";
		})
	}
}
	