import React, { useState } from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import Session from "./Components/Session";
import Telemetry from "./Components/Telemetry";
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
            active={activeTab === "telemetry"}
            onClick={() => handleTabChange("telemetry")}
          >
            Telemetry
          </Tab>
        </TabWrapper>

        <>
          {activeTab === "session" && <Session />}
          {activeTab === "calendar" && <Calendar />}
          {activeTab === "telemetry" && <Telemetry />}
        </>
      </header>
    </PageWrapper>
  );
}

export default App;
