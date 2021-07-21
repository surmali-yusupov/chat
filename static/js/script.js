let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let menuLink = document.getElementById("menu-link");
let userId = document.getElementById("user-id").value;
let userName = document.getElementById("user-nane").value;
let hostname = document.getElementById("hostname").value;
let chatInputBox = document.getElementById('input-box');
let chatInput = document.getElementById('chat-input');
let sendButton = document.getElementById('chat-send-btn');
let sendIcon = document.getElementById('chat-send-icon');
let headerText = document.getElementById('header-text');
let searchInput = document.getElementById("search-input");
let contactBox = document.getElementById("contact-box");
let searchBox = document.getElementById("search-box");
let chatBox = document.getElementById("chat-box");
let userWs = new ReconnectingWebSocket(ws_scheme + "://" + hostname + ":8000/chat/" + userId)
userWs.onmessage = onUserMessage;
let currentChat;
let chats = [];

function setup() {
    let contacts = document.getElementsByClassName("contact");
    let removeBtns = document.getElementsByClassName("remove");
    for (let i = 0; i < contacts.length; i++) {
        contacts[i].firstElementChild.addEventListener("click", openChatBox);
    }
    for (let i = 0; i < contacts.length; i++) {
        createChat(contacts[i].firstElementChild);
    }
    for (let i = 0; i < removeBtns.length; i++) {
        removeBtns[i].addEventListener("click", removeContact);
    }
    sendButton.addEventListener("click", sendMessage);
    document.addEventListener("click", contactMenuEvent);
}

function onChatMessage(event) {
    obj = JSON.parse(event.data);
    if (obj.sender == userId) {
        // TODO mark as delivered...
        return
    }
    let chatMessages = document.getElementById("chat-" + obj["sender"]);
    let message = document.createElement("div");
    message.innerText = obj.text;
    message.className = "chat-message";
    let time = document.createElement("div");
    time.className = "chat-message-time";
    let d = new Date(obj["date"] - new Date().getTimezoneOffset() * 60 * 1000);
    time.innerText = d.getHours() + ":" + ("0" + d.getMinutes()).substr(-2);
    message.append(time);
    chatMessages.append(message);
    window.scroll(0, chatMessages.scrollHeight);
    moveContactUp(obj["sender"]);
}

function onUserMessage(event) {
    let data = JSON.parse(event.data);
    if (data["action"] == "create") {
        let contact = createContact(data["sender"], data["name"]);
        createWS(data["sender"], data["name"]);
        createMessageBox(contact.id);
    } else if (data["action"] == "remove") {
        deleteContact(data["sender"]);
    } else if (data["action"] == "connect") {
        document.getElementById("status-" + data["sender"]).style.fill = "#19dfb1";
    } else if (data["action"] == "disconnect") {
        document.getElementById("status-" + data["sender"]).style.fill = "#dddddd";
    }
}

function contactMenuEvent(e) {
    if (e.target.classList.contains("contact-menu-btn")) {
        e.target.firstElementChild.classList.toggle("show");
    } else {
        let items = document.getElementsByClassName("contact-menu-dropdown");
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove("show");
        }
    }
}

function onEent(event) {
    chatInput.dispatchEvent(new Event("change"));
}

function getChat(id) {
    for (let i = 0; i < chats.length; i++) {
        if (chats[i]["id"] == id) {
            return i;
        }
    }
    return -1;
}

function openChatBox(e) {
    let id = e.target.id;
    let name = e.target.innerText;
    searchBox.innerHTML = "";
    let chatBoxes = document.getElementsByClassName("chat-messages");
    let exists = false;
    for (let i = 0; i < chatBoxes.length; i++) {
        if (chatBoxes[i].id == "chat-" + id) {
            document.getElementById(id).parentElement.classList.add("contact-active");
            currentChat = getChat(id);
            chatInput.value = chats[currentChat]["message"];
            headerText.innerText = chats[currentChat]["name"];
            chatBoxes[i].style.display = "flex";
            chatInputBox.style.display = "flex";
            onEent();
            resetSearch();
            exists = true;
        } else {
            document.getElementById(chatBoxes[i].id.split("-")[1])
                .parentElement.classList.remove("contact-active");
            chatBoxes[i].style.display = "none";
        }
    }
    if (!exists) {
        createMessageBox(id);
        createWS(id, name);
        addToChats(id, name);
        document.getElementById(id).dispatchEvent(new Event("click"));
    }
}

function addToChats(id, name) {
    let xhttp = new XMLHttpRequest();
    let data = JSON.stringify({"sender": userId, "receiver": id, "name": userName, "action": "create"});
    userWs.send(data);
    createContact(id, name);
    xhttp.open("POST", "/api/chat/create", true);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.send(id);
}

function createContact(id, name) {
    let contact = document.createElement("div");
    let contactLink = document.createElement("a");
    let menuBtn = document.createElement("div");
    let menuDrop = document.createElement("div");
    let menuRemove = document.createElement("a");
    let contactStatus = document.createElement("div");
    contact.className = "contact";
    menuBtn.className = "contact-menu-btn col-2";
    contactLink.className = "contact-link col-9";
    contactLink.innerText = name;
    contactLink.href = "#" + name;
    contactLink.id = id;
    contactLink.addEventListener("click", openChatBox);
    menuDrop.className = "contact-menu-dropdown";
    menuDrop.id = id + "-menu";
    menuRemove.className = "contact-menu-entry remove";
    menuRemove.href = "#remove";
    menuRemove.innerText = "Remove";
    menuRemove.addEventListener("click", removeContact);
    contactStatus.className = "col-1";
    contactStatus.innerHTML =
        `<div class="col-1">
            <svg id="status-${id}" viewBox="0 0 100 100" style="width: 0.4rem; height: 0.4rem"
                 xmlns="http://www.w3.org/2000/svg" fill="#dddddd">
                <circle cx="50" cy="50" r="50"></circle>
            </svg>
        </div>`;
    menuDrop.append(menuRemove);
    menuBtn.append(menuDrop);
    contact.append(contactLink);
    contact.append(contactStatus);
    contact.append(menuBtn);
    contactBox.append(contact);
    return contactLink;
}

function removeContact(e) {
    id = e.target.parentElement.id.split("-")[0];
    deleteContact(id);
}

function deleteContact(id) {
    index = getChat(id);
    chats.splice(index, 1);
    if (document.getElementById(id).innerText == headerText.innerText) {
        headerText.innerText = "...";
        chatInputBox.style.display = "none";
    }
    document.getElementById(id).parentElement.remove();
    document.getElementById("chat-" + id).remove();
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/chat/remove", true);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.send(id);
    let data = JSON.stringify({"sender": userId, "receiver": id, "name": userName, "action": "remove"});
    userWs.send(data);
}

function moveContactUp(id) {
    let c = document.getElementById(id).parentElement;
    contactBox.removeChild(c);
    contactBox.prepend(c);
}

function createChat(contact) {
    createWS(contact.id, contact.innerText);
}

function createWS(id, name) {
    obj = {
        "id": id,
        "name": name,
        "room": id < userId ? id.toString() + userId : userId + id,
        "message": ""
    };
    obj["ws"] = new ReconnectingWebSocket(ws_scheme + "://" + hostname + ":8000/chat/" + userId + "/" + obj["room"])
    obj["ws"].onmessage = onChatMessage;
    obj["ws"].onopen = onEent;
    obj["ws"].onerror = onEent;
    obj["ws"].onclose = onEent;
    chats.push(obj);
}

function createMessageBox(id) {
    let newChat = document.createElement("div");
    newChat.className = "chat-messages";
    newChat.id = "chat-" + id;
    chatBox.append(newChat);
}

function sendMessage() {
    let chatMessages = document.getElementById("chat-" + chats[currentChat]["id"]);
    let message = document.createElement('div');
    let time = document.createElement("div");
    message.innerText = chatInput.value;
    message.className = 'chat-message me';
    time.className = "chat-message-time";
    message.append(time);
    chatMessages.append(message);
    window.scroll(0, chatMessages.scrollHeight);
    d = new Date();
    obj = {
        "text": message.innerText,
        "sender": userId,
        "receiver": chats[currentChat]["id"],
        "date": Math.floor((d.getTime())) + (d.getTimezoneOffset() * 60 * 1000)
    };
    time.innerText = d.getHours() + ":" + ("0" + d.getMinutes()).substr(-2);
    data = JSON.stringify(obj);
    chatInput.value = '';
    chatInput.dispatchEvent(new Event("change"));
    chats[currentChat]["ws"].send(data);
    moveContactUp(chats[currentChat]["id"]);
}

function chatInputChange(e) {
    chats[currentChat]["message"] = e.target.value;
    if (e.target.value !== '' && e.target.value != null && chats[currentChat]["ws"].readyState === WebSocket.OPEN) {
        sendButton.disabled = false;
        sendIcon.setAttribute('fill', '#1A8EFF');
    } else {
        sendButton.disabled = true;
        sendIcon.setAttribute('fill', '#B3B7BB');
    }
}

function onEnterPress(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        if (e.target.value !== '' && e.target.value != null && chats[currentChat]["ws"].readyState === WebSocket.OPEN) {
            sendMessage();
        }
    }
}

function resetSearch() {
    searchBox.innerHTML = "";
    searchBox.style.display = "none";
    contactBox.style.display = "flex";
    searchInput.value = "";
}

function searchEvent(event) {
    if (event.target.value.length > 2) {
        let xhttp = new XMLHttpRequest();
        contactBox.style.display = "none";
        searchBox.style.display = "flex";
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                searchBox.innerHTML = "";
                let res = JSON.parse(this.responseText);
                for (let i = 0; i < res.length; i++) {
                    let c = document.createElement("a");
                    c.className = "contact contact-link";
                    c.innerText = res[i]["username"];
                    c.href = "#" + res[i]["username"];
                    c.id = res[i]["id"];
                    c.addEventListener("click", openChatBox);
                    searchBox.append(c);
                }
            }
        };

        xhttp.open("GET", "/api/user/search?q=" + event.target.value, true);
        xhttp.send();
    } else {
        contactBox.style.display = "flex";
        searchBox.style.display = "none";
    }
}

searchInput.addEventListener('input', searchEvent);
chatInput.addEventListener('keydown', onEnterPress);
chatInput.addEventListener('input', chatInputChange);
chatInput.addEventListener('change', chatInputChange);

function getElements() {
    return {
        sidebar: document.getElementById("sidebar"),
        wrapper: document.getElementById("wrapper"),
        header: document.getElementById("header"),
        input: document.getElementById("input-box"),
    };
}

function toggleAll() {
    let elements = getElements();
    elements.wrapper.classList.toggle("active");
    elements.header.classList.toggle("active");
    elements.sidebar.classList.toggle("active");
    elements.input.classList.toggle("active");
}

function handleEvent(e) {
    e.preventDefault();
    toggleAll();
}

menuLink.addEventListener("click", handleEvent);
