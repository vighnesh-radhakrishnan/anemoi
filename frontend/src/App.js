import React, { useState } from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import Session from "./Components/Session";
import FastestLap from "./Components/FastestLap";
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
            active={activeTab === "session"}
            onClick={() => handleTabChange("session")}
          >
            Session Details
          </Tab>
          <Tab
            active={activeTab === "FastestLap"}
            onClick={() => handleTabChange("FastestLap")}
          >
            Fastest Lap
          </Tab>
        </TabWrapper>

        <>
          {activeTab === "session" && <Session />}
          {activeTab === "calendar" && <Calendar />}
          {activeTab === "FastestLap" && <FastestLap />}
        </>
      </header>
    </PageWrapper>
  );
}

export default App;
