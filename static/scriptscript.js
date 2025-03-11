document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loadEvents").addEventListener("click", loadEvents);
    document.getElementById("proceedBtn").addEventListener("click", proceedWithEvents);
});

let selectedEventIds = new Set(); // Use Set to prevent duplicates

function loadEvents() {
    fetch("http://127.0.0.1:8080/api/events")
        .then(response => {
            if (!response.ok) throw new Error("Failed to load events");
            return response.json();
        })
        .then(data => {
            console.log("Events loaded successfully:", data);

            const eventTable = document.getElementById("eventTable");
            eventTable.innerHTML = ""; // Clear table before adding new data

            data.forEach(event => {
                let row = document.createElement("tr");
                row.innerHTML = `
                    <td><input type="checkbox" class="eventCheckbox" value="${event.id}"></td>
                    <td>${event.id}</td>  
                    <td>${event.event_name}</td>
                    <td>${event.location}</td>
                    <td>${event.timing}</td>
                    <td>${event.ticket_price}</td>
                `;
                eventTable.appendChild(row);
            });

            // Attach event listeners to checkboxes after rendering
            document.querySelectorAll(".eventCheckbox").forEach(checkbox => {
                checkbox.addEventListener("change", function () {
                    if (this.checked) {
                        selectedEventIds.add(this.value);
                    } else {
                        selectedEventIds.delete(this.value);
                    }

                    console.log("Selected Event IDs:", Array.from(selectedEventIds));
                    document.getElementById("proceedBtn").disabled = selectedEventIds.size === 0;
                });
            });
        })
        .catch(error => {
            console.error("Could not load events. Please try again.", error);
            alert("Error loading events. Please try again later.");
        });
}

function proceedWithEvents() {
    window.location.href = "http://127.0.0.1:8001/index2"; // Calls FastAPI route in main.p
}
