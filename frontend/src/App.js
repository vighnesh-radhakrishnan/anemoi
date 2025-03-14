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
import { PageWrapper } from "./Components/Container";
import Footer from "./Components/Footer";

import styled from "styled-components";

export const NavContainer = styled.nav`
  width: 100%;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e0e0e0;
`;

export const NavList = styled.ul`
  display: flex;
  justify-content: space-between;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
`;

export const NavItem = styled.li`
  position: relative;

  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background-color: #e10600;
    transform: scaleX(0);
    transition: transform 0.3s ease;
    transform-origin: bottom right;
  }

  ${(props) =>
    props.active &&
    `
    &::after {
      transform: scaleX(1);
      transform-origin: bottom left;
    }
  `}

  &:hover::after {
    transform: scaleX(1);
    transform-origin: bottom left;
  }
`;

export const NavLink = styled.a`
  display: block;
  padding: 1.2rem 1rem;
  color: #333;
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  font-weight: ${(props) => (props.active ? "600" : "400")};
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s;

  &:hover {
    color: #e10600;
  }

  ${(props) =>
    props.active &&
    `
    color: #e10600;
  `}
`;

// Update your App component with the new navigation
function App() {
  const [activeTab, setActiveTab] = useState("calendar");

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <>
      <PageWrapper>
        <header className="App-header">
          <NavContainer>
            <NavList>
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
