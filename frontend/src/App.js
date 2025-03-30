import React, { useState } from "react";
import Calendar from "./Components/Calendar";
import Session from "./Components/Session";
import FastestLap from "./Components/FastestLap";
import Circuits from "./Components/Circuits";
import Standings from "./Components/Standings";
import Constructors from "./Components/Constructors";
import Drivers from "./Components/Drivers";
import TrackDominance from "./Components/TrackDominance";
import DriverComparison from "./Components/DriverComparison";
import {
  PageWrapper,
  NavContainer,
  NavList,
  NavItem,
  NavLink,
  MobileMenuButton,
  Overlay,
} from "./Components/Container";
import { ReactComponent as MenuOpenIcon } from "./Icons/menuOpenIcon.svg";
import { ReactComponent as MenuCloseIcon } from "./Icons/menuCloseIcon.svg";
import Footer from "./Components/Footer";

function App() {
  const [activeTab, setActiveTab] = useState("calendar");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setMobileMenuOpen(false); // Close mobile menu when a tab is selected
  };

  return (
    <>
      <PageWrapper>
        <header className="App-header">
          <NavContainer>
            <MobileMenuButton
              isOpen={mobileMenuOpen}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span></span>
              <span></span>
              <span></span>
            </MobileMenuButton>
            <Overlay
              isOpen={mobileMenuOpen}
              onClick={() => setMobileMenuOpen(false)}
            />
            <NavList isOpen={mobileMenuOpen}>
              <NavItem active={activeTab === "calendar"}>
                <NavLink
                  active={activeTab === "calendar"}
                  onClick={() => handleTabChange("calendar")}
                >
                  Calendar
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "standings"}>
                <NavLink
                  active={activeTab === "standings"}
                  onClick={() => handleTabChange("standings")}
                >
                  Standings
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "session"}>
                <NavLink
                  active={activeTab === "session"}
                  onClick={() => handleTabChange("session")}
                >
                  Session
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "fastestLap"}>
                <NavLink
                  active={activeTab === "fastestLap"}
                  onClick={() => handleTabChange("fastestLap")}
                >
                  Fastest Lap
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "trackdominance"}>
                <NavLink
                  active={activeTab === "trackdominance"}
                  onClick={() => handleTabChange("trackdominance")}
                >
                  Track Dominance
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "drivercomparison"}>
                <NavLink
                  active={activeTab === "drivercomparison"}
                  onClick={() => handleTabChange("drivercomparison")}
                >
                  Driver Comparison
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "circuits"}>
                <NavLink
                  active={activeTab === "circuits"}
                  onClick={() => handleTabChange("circuits")}
                >
                  Circuits
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "constructors"}>
                <NavLink
                  active={activeTab === "constructors"}
                  onClick={() => handleTabChange("constructors")}
                >
                  Constructors
                </NavLink>
              </NavItem>
              <NavItem active={activeTab === "drivers"}>
                <NavLink
                  active={activeTab === "drivers"}
                  onClick={() => handleTabChange("drivers")}
                >
                  Drivers
                </NavLink>
              </NavItem>
            </NavList>
          </NavContainer>
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
