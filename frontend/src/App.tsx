import React, { MouseEventHandler } from "react";
import "./App.css";
import "./iframe-api";
import { string } from "yargs";
declare global {
  interface Window {
    onSpotifyIframeApiReady: any;
  }
}

let IFrameAPI: any = null;

function App() {
  return (
    <>
      <div className="parallax-wrap">
        <div className="background-grid"></div>
      </div>
      <main>
        <div className="top-text">
          <div className="title">
            <h1>
              <span style={{ color: "deepskyblue" }}>Sound</span>Scout
            </h1>
          </div>
          <div className="input-box" onClick={sendFocus}>
            <img src="mag.png" onClick={search} alt="Search" />
            <input placeholder="Search for a playlist" id="filter-text-val" />
          </div>
        </div>
        <div id="iframes">
          <div id="embed-iframe0"></div>
          <div id="embed-iframe1"></div>
          <div id="embed-iframe2"></div>
          <div id="embed-iframe3"></div>
          <div id="embed-iframe4"></div>
          <div id="embed-iframe5"></div>
          <div id="embed-iframe6"></div>
          <div id="embed-iframe7"></div>
          <div id="embed-iframe8"></div>
          <div id="embed-iframe9"></div>
        </div>
        <div id="answer-box"></div>
      </main>
      <footer>
        Created by Harrison Chin, Willy Jiang, Joshua Guo, Eric Huang, Alex
        Levinson
      </footer>
      <script
        src="https://open.spotify.com/embed-podcast/iframe-api/v1"
        async></script>
    </>
  );
}

function answerBoxTemplate(title: string, titleDesc: string) {
  return `<div class='song-title'>${title}</div>`;
}

const sendFocus: MouseEventHandler<HTMLDivElement> = (e) => {
  (document.getElementById("filter-text-val") as HTMLInputElement).focus();
};

const search: MouseEventHandler<HTMLImageElement> = (e) => {
  // (document.getElementById("answer-box") as HTMLDivElement).innerHTML = "";
  const box: HTMLElement = document.getElementById("iframes") as HTMLDivElement;
  while (box.lastElementChild) {
    box.removeChild(box.lastElementChild);
  }
  for (let i = 0; i < 10; i++) {
    const el = document.createElement("div");
    el.setAttribute("id", "embed-iframe" + i);
    box.appendChild(el);
  }
  fetch(
    "http://localhost:5000/search?" +
      new URLSearchParams({
        title: (document.getElementById("filter-text-val") as HTMLInputElement)
          .value,
      }).toString()
  )
    .then((response) => response.json())
    .then((data) =>
      data.forEach((row: string[], i: number) => {
        // each row is [song name, song artist, song uri]
        // for (let i = 0; i < 10; i++) {
        const element = document.getElementById("embed-iframe" + i);
        const options = {
          width: "400",
          height: "150",
          uri: row[2],
        };
        const callback = (EmbedController: any) => {};
        IFrameAPI.createController(element, options, callback);
        // }
      })
    );
};

const parallax = (event: MouseEvent) => {
  const x = (window.innerWidth - event.pageX * 1) / 90;
  const y = (window.innerHeight - event.pageY * 1) / 90;

  (
    document.querySelector(".parallax-wrap .background-grid") as HTMLDivElement
  ).style.transform = `translateX(${x}px) translateY(${y}px)`;
};

document.addEventListener("mousemove", parallax);

window.onSpotifyIframeApiReady = (IFrameApi: any) => {
  IFrameAPI = IFrameApi;
};

export default App;
