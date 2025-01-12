import React, { useState } from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import GetSession from "./Components/GetSession";
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
        </TabWrapper>

        <>
          {activeTab === "session" && <GetSession />}
          {activeTab === "calendar" && <Calendar />}
        </>
      </header>
    </PageWrapper>
  );
}

export default App;
