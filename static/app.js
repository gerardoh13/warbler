const newMsgForm = document.getElementById("newMsgForm");
const messages = document.getElementById("messages");
const userId = document.getElementById("profileLink").dataset.id;

newMsgForm.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!newMsgForm.checkValidity()) {
    newMsgForm.classList.add("was-validated");
    return;
  }
  addMsg();
  newMsgForm.reset();
  newMsgForm.classList.remove("was-validated");
  $("#newMsgModal").modal("hide");
});

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
    `;
}

async function addMsg() {
  let text = document.getElementById("newMsg").value;

  const newMsgRes = await axios.post("/api/messages", { text });
  let newMsg = newMsgRes.data.message;
  if (window.location.pathname === "/" || window.location.pathname === `/users/${userId}`) {
    generateMsg(newMsg);
    $("#messages").prepend(generateMsg(newMsg));
    let msgCount = document.getElementById("msgCount");
    msgCount.innerText = parseInt(msgCount.innerHTML) + 1;
  }
}

$("#newMsgModal").on("shown.bs.modal", () => {
  $("#newMsg").focus();
});

$("#newMsgModal").on("hidden.bs.modal", () => {
  newMsgForm.reset();
});

messages.addEventListener("click", async (e) => {
  if (e.target.tagName === "BUTTON") {
    let msg_id = e.target.dataset.id
    const likeRes = await axios.post("/api/messages/like", { msg_id });
    e.target.classList.toggle("btn-primary")
    e.target.classList.toggle("btn-secondary")
    handleLikeRes(likeRes.data.message)
  }
})

function handleLikeRes(res) {
  let likeCount = document.getElementById("likeCount");
  if (window.location.pathname === "/" || window.location.pathname === `/users/${userId}/likes`) {
    if (res === "liked"){
      likeCount.innerText = parseInt(likeCount.innerHTML) + 1;
    } else {
      likeCount.innerText = parseInt(likeCount.innerHTML) - 1;
    }
  }
}