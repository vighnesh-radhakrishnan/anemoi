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

  @media (max-width: 968px) {
    position: relative;
  }
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

  @media (max-width: 968px) {
    flex-direction: column;
    align-items: flex-start;
    padding-top: 60px;
    transform: ${(props) =>
      props.isOpen ? "translateX(0)" : "translateX(-100%)"};
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 80%;
    background-color: white;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease-in-out;
    z-index: 100;
  }
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

  @media (max-width: 968px) {
    width: 100%;

    &::after {
      bottom: -5px;
      height: 2px;
    }
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

  @media (max-width: 968px) {
    padding: 1rem 2rem;
    width: 100%;
    font-size: 16px;
  }
`;

export const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 1rem;

  @media (max-width: 968px) {
    display: block;
    position: absolute;
    right: 1rem;
    top: 1rem;
    z-index: 101;
  }

  span {
    display: block;
    width: 25px;
    height: 3px;
    margin: 5px 0;
    position: relative;
    background: ${(props) => (props.isOpen ? "#e10600" : "#333")};
    border-radius: 3px;
    z-index: 1;
    transform-origin: 4px 0px;
    transition: transform 0.5s cubic-bezier(0.77, 0.2, 0.05, 1),
      background 0.5s cubic-bezier(0.77, 0.2, 0.05, 1), opacity 0.55s ease;

    &:first-child {
      transform-origin: 0% 0%;
      transform: ${(props) =>
        props.isOpen ? "rotate(45deg) translate(0, -1px)" : "none"};
    }

    &:nth-child(2) {
      opacity: ${(props) => (props.isOpen ? "0" : "1")};
      transform: ${(props) =>
        props.isOpen ? "rotate(0deg) scale(0.2, 0.2)" : "none"};
    }

    &:nth-child(3) {
      transform-origin: 0% 100%;
      transform: ${(props) =>
        props.isOpen ? "rotate(-45deg) translate(0, 1px)" : "none"};
    }
  }
`;

export const Overlay = styled.div`
  display: none;

  @media (max-width: 968px) {
    display: ${(props) => (props.isOpen ? "block" : "none")};
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 99;
  }
`;

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
