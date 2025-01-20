import React, { useState } from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import Session from "./Components/Session";
import FastestLap from "./Components/FastestLap";
import Circuits from "./Components/Circuits";
import Standings from "./Components/Standings";
import { PageWrapper, TabWrapper, Tab } from "./Components/Container";

function App() {
  const [activeTab, setActiveTab] = useState("calendar");

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <PageWrapper>
      <header className="App-header">
        <TabWrapper>
          <Tab
            active={activeTab === "calendar"}
            onClick={() => handleTabChange("calendar")}
          >
            Calendar
          </Tab>
          <Tab
            active={activeTab === "standings"}
            onClick={() => handleTabChange("standings")}
          >
            Standings
          </Tab>
          <Tab
            active={activeTab === "session"}
            onClick={() => handleTabChange("session")}
          >
            Session Details
          </Tab>
          <Tab
            active={activeTab === "fastestLap"}
            onClick={() => handleTabChange("fastestLap")}
          >
            Fastest Lap
          </Tab>
          <Tab
            active={activeTab === "circuits"}
            onClick={() => handleTabChange("circuits")}
          >
            Circuits
          </Tab>
        </TabWrapper>

        <>
          {activeTab === "session" && <Session />}
          {activeTab === "calendar" && <Calendar />}
          {activeTab === "fastestLap" && <FastestLap />}
          {activeTab === "circuits" && <Circuits />}
          {activeTab === "standings" && <Standings />}
        </>
      </header>
    </PageWrapper>
  );
}

export default App;
