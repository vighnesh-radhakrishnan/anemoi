import React from "react";
import ChampionShip from "./Components/ChampionShip"; // Import the Championship component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Formula 1 Championship Winners</h1>
        <ChampionShip /> {/* Use the Championship component here */}
      </header>
    </div>
  );
}

export default App;
