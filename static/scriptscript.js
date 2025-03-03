document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loadEvents").addEventListener("click", loadEvents);
});

let selectedEventIds = [];

function loadEvents() {
    fetch("http://127.0.0.1:8080/api/events")
        .then(response => response.json())
        .then(data => {
            console.log("Events loaded successfully:", data);

            const eventTable = document.getElementById("eventTable");
            eventTable.innerHTML = ""; 

            data.forEach(event => {
                let row = `<tr>
                    <td><input type="checkbox" class="eventCheckbox" value="${event.id}"></td>
                    <td>${event.id}</td>  
                    <td>${event.event_name}</td>
                    <td>${event.location}</td>
                    <td>${event.timing}</td>
                    <td>${event.ticket_price}</td>
                </tr>`;
                eventTable.innerHTML += row;
            });

            // Add event listener to checkboxes after rendering
            document.querySelectorAll(".eventCheckbox").forEach(checkbox => {
                checkbox.addEventListener("change", function () {
                    if (this.checked) {
                        selectedEventIds.push(this.value);
                    } else {
                        selectedEventIds = selectedEventIds.filter(id => id !== this.value);
                    }

                    console.log("Selected Event IDs:", selectedEventIds);

                    // Enable the Proceed button if at least one event is selected
                    document.getElementById("proceedBtn").disabled = selectedEventIds.length === 0;
                });
            });
        })
        .catch(error => console.error("Could not load events. Please try again.", error));
}

document.getElementById("proceedBtn").addEventListener("click", function () {
    if (selectedEventIds.length > 0) {
        console.log("Sending selected event IDs:", selectedEventIds);

        // Send a POST request to FastAPI endpoint to process the event data
        fetch("http://127.0.0.1:8000/process_event", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ event_ids: selectedEventIds })
        })
        .then(response => {
            if (response.ok) {
                return response.json(); // Proceed if the request is successful
            } else {
                throw new Error("Error processing events");
            }
        })
        .then(data => {
            if (data && data.success) {
                console.log("Response:", data);
                alert("Events processed successfully!");

                // Redirect to index2.html and pass event IDs as query parameters using GET
                window.location.href = `/index2?event_ids=${selectedEventIds.join(',')}`;
            }
        })
        .catch(error => console.error("Error sending data:", error));
    } else {
        alert("Please select at least one event before proceeding.");
    }
});
