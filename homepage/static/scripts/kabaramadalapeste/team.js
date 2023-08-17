var jitsi = document.getElementById('jitsi');

const chatFrame = document.createElement("iframe");
chatFrame.src = jitsi.dataset.chatRoomLink;
chatFrame.width = "100%";
chatFrame.height = "300px";
chatFrame.style.border = "none";
chatFrame.style.background = "white";

jitsi.appendChild(chatFrame);
