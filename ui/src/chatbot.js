"use strict";

const url = "http://127.0.0.1:9090";
const context = [];

const history = document.getElementById("history");
const input = document.getElementById("input");
const textbox = document.getElementById("textbox");
const button = document.getElementById("button");

input.addEventListener("submit", event => {
  event.preventDefault();

  if (!textbox.value) return;

  appendMessage("You", "user", textbox.value);
  answer();
});

const appendMessage = async (name, speaker, text) => {
  const img = speaker === "scale"
    ? `<div><img class="scale-img" src="img/logo-chat.svg"></div>`
    : "";
  const msg = `
    <div class="msg ${speaker}-msg">
      ${img}
      <div class="bubble ${speaker}-bubble">
        <div class="name">${name}</div>
        <div class="text">${text}</div>
      </div>
    </div>
  `;

  history.insertAdjacentHTML("beforeend", msg);
  history.scrollTop = history.scrollHeight;

  return msg;
}

const answer = async _ => {
  const question = textbox.value;

  textbox.value = "";
  textbox.disabled = true;
  button.disabled = true;

  const msg = appendMessage("Scale Venture Partners", "scale", "");

  const queryStringParameters = [
    `question=${encodeURIComponent(question)}`,
    `context=${encodeURIComponent(JSON.stringify(context || []))}`
  ];
  const queryString = queryStringParameters.reduce(
    (queryString, queryStringParameter) => `${queryString}&${queryStringParameter}`,
    ""
  ).slice(1);

  const evtSource = new EventSource(`${url}/?${queryString}`);

  evtSource.onmessage = event => {
    const texts = document.getElementsByClassName("text");

    if (event.data != "[DONE]") {
      let chunk = event.data;
      chunk = chunk.replace("\n", "<br>");

      texts[texts.length - 1].innerHTML += chunk;

    } else {
      evtSource.close();

      textbox.disabled = false;
      button.disabled = false;

      context.push({
        question: texts[texts.length - 2].innerHTML.trim(),
        answer: texts[texts.length - 1].innerHTML.trim().replace("<br>", "\n")
      });
    }

    history.scrollTop = history.scrollHeight;
  };

  evtSource.onerror = err => {
    console.error(err);

    evtSource.close();

    const errorMessage = "I was unable to get an answer right now, please try again later.";
    const texts = document.getElementsByClassName("text");
    texts[texts.length - 1].innerHTML = errorMessage;

    textbox.disabled = false;
    button.disabled = false;
  };
}