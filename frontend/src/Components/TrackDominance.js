// src/pages/TrackDominance.jsx
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

const TrackDominance = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [grandPrix, setGrandPrix] = useState("");
  const [sessionIdentifier, setSessionIdentifier] = useState("");
  const [driver1, setDriver1] = useState("");
  const [driver2, setDriver2] = useState("");
  const [dominanceData, setDominanceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(false);
    setDominanceData(null);
    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/track-dominance?year=${selectedYear}&gp=${grandPrix}&identifier=${sessionIdentifier}&driver1=${driver1}&driver2=${driver2}`
      );
      if (response.data.error) {
        setError(true);
        setDominanceData(null);
      } else {
        setError(false);
        setDominanceData(response.data);
      }
    } catch (err) {
      console.error("Error fetching track dominance details:", err);
      setError(true);
      setDominanceData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Track Dominance</h1>
      <FormWrapper onSubmit={handleSubmit} onInput={() => setError(false)}>
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
            marginTop: "70px",
          }}
        >
          <img src={LoadingGif} alt="Loading..." width="150" height="150" />
        </div>
      )}
      {dominanceData && !loading && (
        <div>
          <SessionDetails>
            <div>
              <strong>Grand Prix</strong>
              <span>{dominanceData.gp}</span>
            </div>
            <div>
              <strong>Year</strong>
              <span>{dominanceData.year}</span>
            </div>
            <div>
              <strong>Identifier</strong>
              <span>{dominanceData.identifier}</span>
            </div>
            <div>
              <strong>Driver 1</strong>
              <span>{dominanceData.driver1}</span>
            </div>
            <div>
              <strong>Driver 2</strong>
              <span>{dominanceData.driver2}</span>
            </div>
          </SessionDetails>
          {dominanceData.image_base64 && (
            <div>
              <div className="image-container">
                <img
                  className="image"
                  src={`data:image/png;base64,${dominanceData.image_base64}`}
                  alt="Track Dominance Plot"
                />
              </div>
            </div>
          )}
        </div>
      )}
      {error && !dominanceData && !loading && (
        <NoDataMessage>
          Sorry, no track dominance details found for the provided input. Please
          try again with different values.
        </NoDataMessage>
      )}
    </PageWrapper>
  );
};

export default TrackDominance;
