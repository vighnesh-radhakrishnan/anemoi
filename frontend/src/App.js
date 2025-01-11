import React from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import GetSession from "./Components/GetSession";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <GetSession />
      </header>
    </div>
  );
}

export default App;
