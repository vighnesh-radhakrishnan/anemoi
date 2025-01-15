// @ts-nocheck
import React, { useState } from "react";
import axios from "axios";
import styled from "styled-components";
import { ReactComponent as AvatarIcon } from "../Icons/avatar.svg";
import LoadingGif from "../Icons/loading.gif";
import {
  PageWrapper,
  FormWrapper,
  TableWrapper,
  StyledTable,
  NoDataMessage,
} from "./Container"; // Importing styled divs from `container.js`

const SectionHeading = styled.h2`
  text-align: center;
  margin: 30px 0 20px;
  font-size: 1.5rem;
  color: #333;
`;

const Telemetry = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [grandPrix, setGrandPrix] = useState("");
  const [sessionIdentifier, setSessionIdentifier] = useState("");
  const [telemetryData, setTelemetryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleYearChange = (event) => setSelectedYear(event.target.value);
  const handleGrandPrixChange = (event) => setGrandPrix(event.target.value);
  const handleIdentifierChange = (event) =>
    setSessionIdentifier(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(false);
    setTelemetryData(null);

    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/telemetry?year=${selectedYear}&gp=${grandPrix}&identifier=${sessionIdentifier}`
      );
      if (response.data.error) {
        setError(true);
        setTelemetryData(null);
      } else {
        setError(false);
        setTelemetryData(response.data);
      }
    } catch (err) {
      console.error("Error fetching telemetry data:", err);
      setError(true);
      setTelemetryData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Get Telemetry Data</h1>

      <FormWrapper
        onSubmit={handleSubmit}
        onInput={() => {
          setError(false); // Clear the error message when user modifies input
        }}
      >
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
          placeholder="Enter Session Identifier (e.g., Race)"
          value={sessionIdentifier}
          onChange={handleIdentifierChange}
          required
        />
        <button type="submit">Get Telemetry</button>
      </FormWrapper>

      {loading && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginTop: "50px",
          }}
        >
          <img src={LoadingGif} alt="Loading..." width="150" height="150" />
        </div>
      )}

      {telemetryData && telemetryData.results && loading !== true && (
        <div>
          <SectionHeading>Telemetry Overview</SectionHeading>

          {telemetryData.results.length > 0 ? (
            <TableWrapper>
              <StyledTable>
                <thead>
                  <tr>
                    <th>Driver</th>
                    <th>Speed</th>
                    <th>RPM</th>
                    <th>Gear</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {telemetryData.results.map((telemetry, index) => (
                    <tr key={index}>
                      <td>
                        <div className="driver-info">
                          {telemetry.HeadshotUrl !== "None" &&
                          telemetry.HeadshotUrl !== "" ? (
                            <img
                              src={telemetry.HeadshotUrl}
                              alt={telemetry.DriverName.toLowerCase()}
                            />
                          ) : (
                            <AvatarIcon />
                          )}
                          <span>{telemetry.DriverName}</span>
                        </div>
                      </td>
                      <td>{telemetry.Speed} km/h</td>
                      <td>{telemetry.RPM}</td>
                      <td>{telemetry.Gear}</td>
                      <td>{telemetry.Status || "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </StyledTable>
            </TableWrapper>
          ) : (
            <NoDataMessage>
              No telemetry data available for this session.
            </NoDataMessage>
          )}
        </div>
      )}
      {error && !telemetryData && !loading && (
        <NoDataMessage>
          Sorry, no telemetry data found for the provided input. Please try
          again with different values.
        </NoDataMessage>
      )}
    </PageWrapper>
  );
};

export default Telemetry;
