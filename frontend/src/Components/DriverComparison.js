// src/pages/DriverComparison.jsx
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
import RaceDataForm from "./RaceDataForm";

const DriverComparison = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [grandPrix, setGrandPrix] = useState("");
  const [sessionIdentifier, setSessionIdentifier] = useState("");
  const [driver1, setDriver1] = useState("");
  const [driver2, setDriver2] = useState("");
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(false);
    setComparisonData(null);
    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/driver-comparison?year=${selectedYear}&gp=${grandPrix}&identifier=${sessionIdentifier}&driver1=${driver1}&driver2=${driver2}&stint=${1}`
      );
      if (response.data.error) {
        setError(true);
        setComparisonData(null);
      } else {
        setError(false);
        setComparisonData(response.data);
      }
    } catch (err) {
      console.error("Error fetching driver comparison details:", err);
      setError(true);
      setComparisonData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Driver Comparison Analysis</h1>
      <FormWrapper onInput={() => setError(false)}>
        <RaceDataForm
          selectedYear={selectedYear}
          setSelectedYear={setSelectedYear}
          grandPrix={grandPrix}
          setGrandPrix={setGrandPrix}
          sessionIdentifier={sessionIdentifier}
          setSessionIdentifier={setSessionIdentifier}
          driver1={driver1}
          setDriver1={setDriver1}
          driver2={driver2}
          setDriver2={setDriver2}
          handleSubmit={handleSubmit}
        />
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
      {comparisonData && !loading && (
        <div>
          <SessionDetails>
            <div>
              <strong>Grand Prix</strong>
              <span>{comparisonData.gp}</span>
            </div>
            <div>
              <strong>Year</strong>
              <span>{comparisonData.year}</span>
            </div>
            <div>
              <strong>Identifier</strong>
              <span>{comparisonData.identifier}</span>
            </div>
            <div>
              <strong>Driver 1</strong>
              <span>{comparisonData.driver1}</span>
            </div>
            <div>
              <strong>Driver 2</strong>
              <span>{comparisonData.driver2}</span>
            </div>
            {comparisonData.closest_lap && (
              <div>
                <strong>Closest Battle Lap</strong>
                <span>{comparisonData.closest_lap}</span>
              </div>
            )}
          </SessionDetails>
          {comparisonData.image_base64 && (
            <div>
              <h2 className="image-header">
                Driver Comparison: {comparisonData.driver1} vs{" "}
                {comparisonData.driver2}
              </h2>
              <div className="image-container">
                <img
                  className="image"
                  src={`data:image/png;base64,${comparisonData.image_base64}`}
                  alt="Driver Comparison Plot"
                />
              </div>
            </div>
          )}
        </div>
      )}
      {error && !comparisonData && !loading && (
        <NoDataMessage>
          Sorry, no driver comparison data found for the provided input. Please
          try again with different values or check if both drivers were on track
          during the same stint.
        </NoDataMessage>
      )}
    </PageWrapper>
  );
};

export default DriverComparison;
