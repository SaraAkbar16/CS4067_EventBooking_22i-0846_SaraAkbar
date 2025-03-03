const API_URL = "http://127.0.0.1:8000";

async function fetchUsers() {
    const response = await fetch(`${API_URL}/users/`);
    const users = await response.json();
    
    let list = document.getElementById("usersList");
    list.innerHTML = "";
    
    users.forEach(user => {
        let li = document.createElement("li");
        li.textContent = `${user.id}: ${user.name}`;
        list.appendChild(li);
    });
}

async function addUser() {
    let name = document.getElementById("nameInput").value;
    if (!name) return alert("Enter a name");
    
    const response = await fetch(`${API_URL}/users/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
    });

    if (response.ok) {
        fetchUsers();
    }
}

fetchUsers();
