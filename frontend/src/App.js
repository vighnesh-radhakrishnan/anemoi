import React, { useState } from "react";
import Calendar from "./Components/Calendar"; // Import the Championship component
import Session from "./Components/Session";
import FastestLap from "./Components/FastestLap";
import Circuits from "./Components/Circuits";
import Standings from "./Components/Standings";
import Constructors from "./Components/Constructors";
import Drivers from "./Components/Drivers";
import TrackDominance from "./Components/TrackDominance";
import DriverComparison from "./Components/DriverComparison";
import { PageWrapper, TabWrapper, Tab } from "./Components/Container";
import Footer from "./Components/Footer";

function App() {
  const [activeTab, setActiveTab] = useState("calendar");

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <>
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
              active={activeTab === "trackdominance"}
              onClick={() => handleTabChange("trackdominance")}
            >
              Track Dominance
            </Tab>
            <Tab
              active={activeTab === "drivercomparison"}
              onClick={() => handleTabChange("drivercomparison")}
            >
              Driver Comparison
            </Tab>
            <Tab
              active={activeTab === "circuits"}
              onClick={() => handleTabChange("circuits")}
            >
              Circuits
            </Tab>
            <Tab
              active={activeTab === "constructors"}
              onClick={() => handleTabChange("constructors")}
            >
              Constructors
            </Tab>
            <Tab
              active={activeTab === "drivers"}
              onClick={() => handleTabChange("drivers")}
            >
              Drivers
            </Tab>
          </TabWrapper>

          <>
            {activeTab === "session" && <Session />}
            {activeTab === "calendar" && <Calendar />}
            {activeTab === "fastestLap" && <FastestLap />}
            {activeTab === "trackdominance" && <TrackDominance />}
            {activeTab === "drivercomparison" && <DriverComparison />}
            {activeTab === "circuits" && <Circuits />}
            {activeTab === "standings" && <Standings />}
            {activeTab === "constructors" && <Constructors />}
            {activeTab === "drivers" && <Drivers />}
          </>
        </header>
      </PageWrapper>
      <Footer />
    </>
  );
}

export default App;
