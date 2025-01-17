// @ts-nocheck
import React, { useState } from "react";
import axios from "axios";
import LoadingGif from "../Icons/loading.gif";
import {
  PageWrapper,
  FormWrapper,
  NoDataMessage,
  SessionDetails,
} from "./Container";

const TelemetryDetails = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [grandPrix, setGrandPrix] = useState("");
  const [sessionIdentifier, setSessionIdentifier] = useState("");
  const [driver, setDriver] = useState("");
  const [telemetryData, setTelemetryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleYearChange = (event) => setSelectedYear(event.target.value);
  const handleGrandPrixChange = (event) => setGrandPrix(event.target.value);
  const handleIdentifierChange = (event) =>
    setSessionIdentifier(event.target.value);
  const handleDriverChange = (event) => setDriver(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(false);
    setTelemetryData(null);

    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/telemetry?year=${selectedYear}&gp=${grandPrix}&identifier=${sessionIdentifier}&driver=${driver}`
      );
      if (response.data.error) {
        setError(true);
        setTelemetryData(null);
      } else {
        setError(false);
        setTelemetryData(response.data);
      }
    } catch (err) {
      console.error("Error fetching telemetry details:", err);
      setError(true);
      setTelemetryData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Telemetry Details</h1>

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
        <input
          type="text"
          placeholder="Enter Driver (e.g., HAM)"
          value={driver}
          onChange={handleDriverChange}
          required
        />
        <button type="submit">Get Telemetry Details</button>
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

      {telemetryData && !loading && (
        <div>
          <SessionDetails>
            <div>
              <strong>Grand Prix:</strong>
              <span>{telemetryData.session.GrandPrix}</span>
            </div>
            <div>
              <strong>Year:</strong>
              <span>{telemetryData.session.Year}</span>
            </div>
            <div>
              <strong>Session:</strong>
              <span>{telemetryData.session.Session}</span>
            </div>
            <div>
              <strong>Driver:</strong>
              <span>{telemetryData.session.Driver}</span>
            </div>
            <div>
              <strong>Event:</strong>
              <span>{telemetryData.session.Event}</span>
            </div>
            <div>
              <strong>Location:</strong>
              <span>{telemetryData.session.Location}</span>
            </div>
          </SessionDetails>

          {telemetryData.image_base64 && (
            <div>
              <h2 className="image-header">
                {telemetryData.session.GrandPrix} Fastest Lap:{" "}
                {telemetryData.session.Driver}
              </h2>
              <img
                src={`data:image/png;base64,${telemetryData.image_base64}`}
                alt="Fastest Lap Telemetry"
              />
            </div>
          )}
        </div>
      )}

      {error && !telemetryData && !loading && (
        <NoDataMessage>
          Sorry, no telemetry details found for the provided input. Please try
          again with different values.
        </NoDataMessage>
      )}
    </PageWrapper>
  );
};

export default TelemetryDetails;
