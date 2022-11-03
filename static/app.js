const newMsgForm = document.getElementById("newMsgForm");
const messages = document.getElementById("messages");

newMsgForm.addEventListener(
  "submit",
  (e) => {
    e.preventDefault();
    if (!newMsgForm.checkValidity()) {
      e.stopPropagation();
      newMsgForm.classList.add("was-validated");
      return;
    }
    addMsg();
    newMsgForm.reset();
    newMsgForm.classList.remove("was-validated");
    $("#newMsgModal").modal("hide");
  },
  false
);

function generateMsg(msg) {
    return `
    <li class="list-group-item">
    <a href="/messages/${msg.id}" class="message-link" />
    <a href="/users/${msg.user.id}">
      <img src="${msg.user.image_url}" alt="" class="timeline-image" />
    </a>
    <div class="message-area">
      <a href="/users/${msg.user.id}">@${msg.user.username}</a>
      <span class="text-muted"
        >${msg.timestamp}</span
      >
      <p class="mt-2">${msg.text}</p>
    </div>
  </li>
    `
}

async function addMsg() {
  let text = document.getElementById("newMsg").value;

  const newMsgRes = await axios.post("/api/messages", {text});
  let newMsg = newMsgRes.data.message;
  if (document.getElementById("sidebar-username")){
    userId = document.getElementById("sidebar-username").dataset.id
  }
  if (window.location.pathname === "/"){
    generateMsg(newMsg)
    $("#messages").prepend(generateMsg(newMsg));
    let count = document.getElementById('homeMsgCount')
    count.innerText = (parseInt(count.innerHTML) + 1)
  } else if (window.location.pathname === `/users/${userId}`){
    generateMsg(newMsg)
    $("#messages").prepend(generateMsg(newMsg));
    let count = document.getElementById('detailMsgCount')
    count.innerText = (parseInt(count.innerHTML) + 1)
  }
}
