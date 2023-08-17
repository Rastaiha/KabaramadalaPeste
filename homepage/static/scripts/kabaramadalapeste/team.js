var jitsi = document.getElementById('jitsi');

const chatFrame = document.createElement("iframe");
chatFrame.src = jitsi.chat_room_link;
chatFrame.width = "400";
chatFrame.height = "100";
chatFrame.style.border = "none";
chatFrame.style.background = "white";

jitsi.appendChild(chatFrame);
