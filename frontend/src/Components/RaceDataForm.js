// src/components/RaceDataForm.jsx
import React from "react";
import styled from "styled-components";

// Add styling for form elements
const FormContainer = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;

  input {
    padding: 12px;
    border-radius: 4px;
    border: 1px solid #ccc;
    font-size: 16px;
  }

  button {
    padding: 12px;
    background-color: #e10600;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;

    &:hover {
      background-color: #b30500;
    }
  }
`;

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
  const handleStintChange = (event) => setStint(event.target.value);

  return (
    <FormContainer onSubmit={handleSubmit}>
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
      {showStint && (
        <input
          type="number"
          placeholder="Enter Stint Number (default: 1)"
          value={stint}
          onChange={handleStintChange}
        />
      )}
      <button type="submit">Get Plot</button>
    </FormContainer>
  );
};

export default RaceDataForm;
