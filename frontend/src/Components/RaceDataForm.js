import React from "react";
import styled from "styled-components";

const RaceDataForm = ({
  selectedYear,
  setSelectedYear,
  grandPrix,
  setGrandPrix,
  sessionIdentifier,
  setSessionIdentifier,
  driver1,
  setDriver1,
  driver2,
  setDriver2,
  stint,
  setStint,
  showStint = false,
  handleSubmit,
}) => {
  const handleYearChange = (event) => setSelectedYear(event.target.value);
  const handleGrandPrixChange = (event) => setGrandPrix(event.target.value);
  const handleIdentifierChange = (event) =>
    setSessionIdentifier(event.target.value);
  const handleDriver1Change = (event) => setDriver1(event.target.value);
  const handleDriver2Change = (event) => setDriver2(event.target.value);

  const handleButtonClick = () => {
    // Create a synthetic event object since handleSubmit expects an event
    const syntheticEvent = { preventDefault: () => {} };
    handleSubmit(syntheticEvent);
  };

  return (
    <div className="race-data" style={{ display: "flex", gap: "15px" }}>
      <input
        type="number"
        placeholder="Enter Year"
        value={selectedYear}
        onChange={handleYearChange}
        required
      />
      <input
        type="text"
        placeholder="Enter Grand Prix Name"
        value={grandPrix}
        onChange={handleGrandPrixChange}
        required
      />
      <input
        type="text"
        placeholder="Enter Session Identifier"
        value={sessionIdentifier}
        onChange={handleIdentifierChange}
        required
      />
      <input
        type="text"
        placeholder="Enter Driver 1 (e.g, HAM)"
        value={driver1}
        onChange={handleDriver1Change}
        required
      />
      <input
        type="text"
        placeholder="Enter Driver 2 (e.g, VER)"
        value={driver2}
        onChange={handleDriver2Change}
        required
      />
      <button type="button" onClick={handleButtonClick}>
        Get Plot
      </button>
    </div>
  );
};

export default RaceDataForm;
