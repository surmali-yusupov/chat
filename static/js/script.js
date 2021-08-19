let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let menuLink = document.getElementById("menu-link");
let userId = +document.getElementById("user-id").value;
let groupCreateModal = document.getElementById("group-create-modal");
let groupCreateContent = document.getElementById("group-create-content");
let groupCreateNameInput = document.getElementById("group-name-input");
let userName = document.getElementById("user-nane").value;
let hostname = document.getElementById("hostname").value;
let chatInputBox = document.getElementById('input-box');
let chatInput = document.getElementById('chat-input');
let userInfoBtn = document.getElementById("user-menu-btn");
let sendButton = document.getElementById('chat-send-btn');
let sendIcon = document.getElementById('chat-send-icon');
let headerText = document.getElementById('header-text');
let searchInput = document.getElementById("search-input");
let chatsBox = document.getElementById("chats-box");
let searchBox = document.getElementById("search-box");
let chatBox = document.getElementById("chat-box");
let userWs = new ReconnectingWebSocket(ws_scheme + "://" + hostname + ":8000/chat/" + userId)
let PRIVATETYPE = +document.getElementById("chat-type-private").value;
let GROUPTYPE = +document.getElementById("chat-type-group").value;
let CONNECTACTION = +document.getElementById("chat-action-connect").value;
let DISCONNECTACTION = +document.getElementById("chat-action-disconnect").value;
let CREATEACTION = +document.getElementById("chat-action-create").value;
let REMOVEACTION = +document.getElementById("chat-action-remove").value;
let LEAVEACTION = +document.getElementById("chat-action-leave").value;
userWs.onmessage = onUserMessage;
let currentChat;
let chats = [];

function setup() {
    let contacts = document.getElementsByClassName("contact");
    let removeBtns = document.getElementsByClassName("remove-btn");
    let groupCreateModalBtn = document.getElementById("group-create-modal-btn");
    let groupCreateBtn = document.getElementById("group-create-btn");
    let modalCloseButtons = document.getElementsByClassName("modal-close");
    for (let i = 0; i < contacts.length; i++) {
        contacts[i].firstElementChild.addEventListener("click", openChatBox);
    }
    for (let i = 0; i < modalCloseButtons.length; i++) {
        modalCloseButtons[i].addEventListener("click", modalClose);
    }
    for (let i = 0; i < contacts.length; i++) {
        createChat(contacts[i].firstElementChild);
    }
    for (let i = 0; i < removeBtns.length; i++) {
        removeBtns[i].addEventListener("click", removeContact);
    }
    groupCreateBtn.addEventListener("click", createGroup);
    sendButton.addEventListener("click", sendMessage);
    groupCreateModalBtn.addEventListener("click", opencreateGroupModal);
    document.addEventListener("click", documentEvent);
}

function onUserMessage(event) {
    let data = JSON.parse(event.data);
    if (data["action"] == CREATEACTION) {
        let contact = createContact(data["id"], data["sender"], data["name"], data["type"]);
        createWS(contact.id, data["name"], data["participants"]);
        createMessageBox(contact.id);
    } else if (data["action"] == REMOVEACTION) {
        deleteContact(data["id"]);
    } else if (data["action"] == CONNECTACTION) {
        document.getElementById("status-" + data["sender"]).style.fill = "#19dfb1";
    } else if (data["action"] == DISCONNECTACTION) {
        document.getElementById("status-" + data["sender"]).style.fill = "#dddddd";
    }
}

function documentEvent(e) {
    let items = document.getElementsByClassName("contact-menu-btn");
    for (let i = 0; i < items.length; i++) {
        if (e.target == items[i]) {
            e.target.firstElementChild.classList.toggle("show");
        } else {
            items[i].firstElementChild.classList.remove("show");
        }
    }
    if (e.target == userInfoBtn) {
        e.target.firstElementChild.classList.toggle("show");
    } else {
        userInfoBtn.firstElementChild.classList.remove("show");
    }
    if (e.target.classList.contains("modal-overlay")) {
        e.target.style.visibility = "hidden";
    }
}

function onChatMessage(event) {
    obj = JSON.parse(event.data);
    if (obj.sender == userId) {
        // TODO mark as delivered...
        return
    }
    let chat = document.getElementById(obj["chat"]);
    let chatMessages = document.getElementById("chat-" + obj["chat"]);
    let message = document.createElement("div");
    if (chat.dataset.type == GROUPTYPE) {
        let username = document.createElement("div");
        username.innerText = obj["username"];
        username.className = "chat-message-username";
        message.append(username);
    }
    message.append(obj.text);
    message.className = "chat-message";
    let time = document.createElement("div");
    time.className = "chat-message-time";
    let d = new Date(obj["date"] - new Date().getTimezoneOffset() * 60 * 1000);
    time.innerText = d.getHours() + ":" + ("0" + d.getMinutes()).substr(-2);
    message.append(time);
    chatMessages.append(message);
    window.scroll(0, chatMessages.scrollHeight);
    moveContactUp(obj["chat"]);
}

function sendMessage() {
    let chatMessages = document.getElementById("chat-" + chats[currentChat]["id"]);
    let message = document.createElement('div');
    let time = document.createElement("div");
    message.append(chatInput.value);
    message.className = 'chat-message me';
    time.className = "chat-message-time";
    message.append(time);
    chatMessages.append(message);
    window.scroll(0, chatMessages.scrollHeight);
    d = new Date();
    obj = {
        "chat": chats[currentChat]["id"],
        "text": message.innerText,
        "sender": userId,
        "username": userName,
        "date": Math.floor((d.getTime())) + (d.getTimezoneOffset() * 60 * 1000)
    };
    time.innerText = d.getHours() + ":" + ("0" + d.getMinutes()).substr(-2);
    data = JSON.stringify(obj);
    chatInput.value = '';
    chatInput.dispatchEvent(new Event("change"));
    chats[currentChat]["ws"].send(data);
    moveContactUp(chats[currentChat]["id"]);
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

function opencreateGroupModal(e) {
    groupCreateModal.style.visibility = "visible";
}

function createGroup(e) {
    let selected = document.querySelectorAll(".group-checkbox:checked");
    let participants = [];
    let name = groupCreateNameInput.value.trim();
    for (let i = 0; i < selected.length; i++) {
        participants.push(+selected[i].id.split("-")[1]);
    }
    if (name != "" && name != null && participants.length > 0) {
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let res = JSON.parse(this.responseText);
                let chat = createContact(res["id"], userId, name, GROUPTYPE);
                createMessageBox(chat.id);
                createWS(chat.id, name, participants);
                document.getElementById(chat.id).dispatchEvent(new Event("click"));
            }
        }
        xhttp.open("POST", "/api/chat/create", true);
        xhttp.setRequestHeader('Content-type', 'application/json');
        let data = JSON.stringify({
            "participants": participants,
            "name": name,
            "type": GROUPTYPE
        });
        xhttp.send(data);
        resetGroupCreateModal();
    }
}

function openChatBox(e) {
    let id = e.target.id;
    searchBox.innerHTML = "";
    let chatBoxes = document.getElementsByClassName("chat-messages");
    for (let i = 0; i < chatBoxes.length; i++) {
        if (chatBoxes[i].id == "chat-" + id) {
            document.getElementById(id).parentElement.classList.add("contact-active");
            currentChat = getChat(id);
            if (currentChat >= 0) {
                headerText.innerText = chats[currentChat]["name"];
                chatBoxes[i].style.display = "flex";
                chatInputBox.style.display = "flex";
                chatInput.value = chats[currentChat]["message"];
            }
            onEent();
            resetSearch();
        } else {
            document.getElementById(chatBoxes[i].id.split("-")[1])
                .parentElement.classList.remove("contact-active");
            chatBoxes[i].style.display = "none";
        }
    }
}

function addToChats(id, name) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let res = JSON.parse(this.responseText);
            let chat = createContact(res["id"], id, name);
            createMessageBox(chat.id);
            createWS(chat.id, name, [+id]);
            document.getElementById(chat.id).dispatchEvent(new Event("click"));
        }
    }
    let chatData = JSON.stringify({"name": userName, "participants": [+id]});
    xhttp.open("POST", "/api/chat/create", true);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.send(chatData);
}

function createContact(id, contactId, name, type = PRIVATETYPE) {
    let chat = document.createElement("div");
    let contactLink = document.createElement("a");
    let menuBtn = document.createElement("div");
    let menuDrop = document.createElement("div");
    let menuRemove = document.createElement("span");
    chat.className = "contact";
    menuBtn.className = "contact-menu-btn col-2";
    contactLink.classList.add("contact-link");
    contactLink.dataset.userId = contactId;
    contactLink.dataset.type = type;
    contactLink.innerText = name;
    contactLink.href = "#" + name;
    contactLink.id = id;
    contactLink.addEventListener("click", openChatBox);
    menuDrop.className = "contact-menu-dropdown";
    menuDrop.id = "menu-" + id;
    if (type == GROUPTYPE) {
        let infoBtn = document.createElement('span');
        infoBtn.className = "contact-menu-entry info-btn";
        infoBtn.innerText = "Info";
        menuDrop.append(infoBtn);
    }
    menuRemove.className = "contact-menu-entry remove-btn";
    menuRemove.innerText = type == PRIVATETYPE ? "Remove" : contactId == userId ? "Remove" : "Leave Group";
    menuRemove.addEventListener("click", removeContact);
    let contactStatus = document.createElement("div");
    if (type == PRIVATETYPE) {
        contactLink.classList.add("col-9");
        contactStatus.className = "col-1";
        contactStatus.innerHTML =
            `<svg id="status-${contactId}" viewBox="0 0 100 100" style="width: 0.4rem; height: 0.4rem"
             xmlns="http://www.w3.org/2000/svg" fill="#dddddd">
                <circle cx="50" cy="50" r="50"></circle>
             </svg>`;
        let contactCheckbox = document.createElement("div");
        contactCheckbox.className = "checkbox-container";
        contactCheckbox.id = "contact-" + contactId;
        contactCheckbox.innerHTML =
            `<input id="check-${contactId}" type="checkbox" class="custom-checkbox group-checkbox">
            <label for="check-${contactId}" class="checkbox-label"
                   style="flex-grow: 1">${name}</label>`;
        groupCreateContent.append(contactCheckbox);
    } else {
        contactLink.classList.add("col-10");
    }
    menuDrop.append(menuRemove);
    menuBtn.append(menuDrop);
    chat.append(contactLink);
    if (type == PRIVATETYPE) {
        chat.append(contactStatus);
    }
    chat.append(menuBtn);
    chatsBox.append(chat);
    return contactLink;
}

function removeContact(e) {
    let id = e.target.parentElement.id.split("-")[1];
    sendRemoveUserMessage(id);
    deleteContact(id);
}

function deleteContact(id) {
    let index = getChat(id);
    let contact = document.getElementById(id);
    if (contact.dataset.type == PRIVATETYPE) {
        document.getElementById("contact-" + contact.dataset.userId).remove();
    }
    if (index >= 0) {
        chats.splice(index, 1);
        if (document.getElementById(id).innerText == headerText.innerText) {
            headerText.innerText = "...";
            chatInputBox.style.display = "none";
        }
        document.getElementById(id).parentElement.remove();
        document.getElementById("chat-" + id).remove();
    }
}

function sendRemoveUserMessage(id) {
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/api/chat/remove", true);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.send(id);
}

function moveContactUp(id) {
    let c = document.getElementById(id).parentElement;
    chatsBox.removeChild(c);
    chatsBox.prepend(c);
}

function createChat(chat) {
    createWS(chat.id, chat.innerText, [+chat.dataset.userId]);
}

function createWS(id, name, participants = null) {
    let obj = {
        "id": +id,
        "name": name,
        "message": "",
        "participants": participants
    };
    obj["ws"] = new ReconnectingWebSocket(ws_scheme + "://" + hostname + ":8000/chat/" + userId + "/" + obj["id"])
    obj["ws"].onmessage = onChatMessage;
    obj["ws"].onopen = onEent;
    obj["ws"].onerror = onEent;
    obj["ws"].onclose = onEent;
    chats.push(obj);
}

function createMessageBox(id) {
    let newChat = document.createElement("div");
    newChat.style.display = "none";
    newChat.id = "chat-" + id;
    newChat.className = "chat-messages";
    chatBox.append(newChat);
}

function chatInputChange(e) {
    let msg = e.target.value.trim();
    chats[currentChat]["message"] = msg;
    if (msg !== '' && msg != null && chats[currentChat]["ws"].readyState === WebSocket.OPEN) {
        sendButton.disabled = false;
        sendIcon.setAttribute('fill', '#44a2ff');
        // sendIcon.setAttribute('fill', '#00caab');
    } else {
        sendButton.disabled = true;
        sendIcon.setAttribute('fill', '#B3B7BB');
    }
}

function onEnterPress(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        let msg = e.target.value.trim();
        if (msg !== '' && msg != null && chats[currentChat]["ws"].readyState === WebSocket.OPEN) {
            sendMessage();
        }
    }
}

function resetGroupCreateModal() {
    groupCreateNameInput.value = "";
    groupCreateModal.style.visibility = "hidden";
    let selected = document.querySelectorAll(".group-checkbox:checked");
    for (let i = 0; i < selected.length; i++) {
        selected[i].checked = false;
    }
}

function resetSearch() {
    searchBox.innerHTML = "";
    searchBox.style.display = "none";
    chatsBox.style.display = "flex";
    searchInput.value = "";
}

function searchEvent(event) {
    if (event.target.value.length > 0) {
        let xhttp = new XMLHttpRequest();
        chatsBox.style.display = "none";
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
                    c.addEventListener("click", searchForChat);
                    searchBox.append(c);
                }
            }
        };
        xhttp.open("GET", "/api/user/search?q=" + event.target.value, true);
        xhttp.send();
    } else {
        chatsBox.style.display = "flex";
        searchBox.style.display = "none";
    }
}

function searchForChat(e) {
    let id = e.target.id;
    let name = e.target.innerText;
    let contacts = document.getElementsByClassName("contact-link");
    for (let i = 0; i < contacts.length; i++) {
        if (contacts[i].dataset.type == PRIVATETYPE) {
            if (contacts[i].dataset.userId == id) {
                document.getElementById(contacts[i].id).dispatchEvent(new Event("click"));
                return;
            }
        }
    }
    addToChats(id, name);
}

function modalClose(e) {
    e.target.closest(".modal-overlay").style.visibility = "hidden";
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
