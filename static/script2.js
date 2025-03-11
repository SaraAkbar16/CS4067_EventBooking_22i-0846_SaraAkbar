document.getElementById("eventForm").addEventListener("submit", function(event) {
    event.preventDefault();  // ✅ Prevent form from refreshing

    let formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("payment", document.getElementById("payment").value);
    formData.append("event", document.getElementById("event").value); // ✅ Ensure name="event"

    fetch("/submit_form/", {  // ✅ Matches backend route
        method: "POST",
        body: formData,  
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("🎉 Booking saved successfully!\n" + 
                  "Name: " + data.data.name + "\n" + 
                  "Payment: " + data.data.payment + "\n" + 
                  "Event ID: " + data.data.event);  // ✅ Show confirmation alert

            document.getElementById("eventForm").reset();  // ✅ Clear form after success
        } else {
            alert(" Error saving booking: " + data.message);  // ✅ Show error alert
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert(" Error submitting the form.");
    });
});
