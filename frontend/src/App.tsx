import React, { MouseEventHandler } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="full-body-container">
    <div className="parallax-wrap">
      <div className="background-grid"></div>
    </div>
    <div className="top-text">
      <div className="title">
        <h1>SoundScout</h1>
      </div>
      <div className="input-box" onClick={sendFocus}>
        <img src="mag.png" onClick={search} />
        <input placeholder="Search for a playlist" id="filter-text-val" />
      </div>
    </div>
    <div id="answer-box"></div>
    <footer>Created by Harrison Chin, Willy Jiang, Joshua Guo, Eric Huang, Alex Levinson</footer>
  </div>
  );
}

function answerBoxTemplate(title: string, titleDesc: string) {
  return `<div class='song-title'>${title}</div>`
}

const sendFocus: MouseEventHandler<HTMLDivElement> = (e) => {
  (document.getElementById("filter-text-val") as HTMLInputElement).focus()
  // this.getElementById("filter-text-val").focus()
}

const search: MouseEventHandler<HTMLImageElement> = (e) => {
  (document.getElementById("answer-box") as HTMLDivElement).innerHTML = ""
  // console.log(document.getElementById("filter-text-val").value)
  const box: HTMLElement = document.getElementById("answer-box") as HTMLDivElement
  while (box.lastElementChild) {
    box.removeChild(box.lastElementChild)
  }
  fetch(
    "http://localhost:8091/search?" +
      new URLSearchParams({ title: (document.getElementById("filter-text-val") as HTMLInputElement).value }).toString()
  )
    .then((response) => response.json())
    .then((data) =>
      data.forEach((row: string[]) => {
        let tempDiv = document.createElement("div")
        tempDiv.className = "answer"
        tempDiv.innerHTML = answerBoxTemplate(row[0], row[3]);
        (document.getElementById("answer-box") as HTMLDivElement).appendChild(tempDiv)
      })
    )
}

const parallax = (event: MouseEvent) => {
  const x = (window.innerWidth - event.pageX * 1) / 90;
  const y = (window.innerHeight - event.pageY * 1) / 90;

  (document.querySelector(".parallax-wrap .background-grid") as HTMLDivElement).style.transform = `translateX(${x}px) translateY(${y}px)`
}

document.addEventListener("mousemove", parallax)

export default App;
