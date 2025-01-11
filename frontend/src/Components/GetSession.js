import React, { useState } from "react";
import axios from "axios";
import styled from "styled-components";
import { ReactComponent as AvatarIcon } from "../Icons/avatar.svg";
import {
  PageWrapper,
  FormWrapper,
  TableWrapper,
  StyledTable,
  SessionDetails,
} from "./Container"; // Importing styled divs from `container.js`

const SectionHeading = styled.h2`
  text-align: center;
  margin: 30px 0 20px;
  font-size: 1.5rem;
  color: #333;
`;

const GetSession = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [grandPrix, setGrandPrix] = useState("");
  const [sessionIdentifier, setSessionIdentifier] = useState("");
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleYearChange = (event) => setSelectedYear(event.target.value);
  const handleGrandPrixChange = (event) => setGrandPrix(event.target.value);
  const handleIdentifierChange = (event) =>
    setSessionIdentifier(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `http://localhost:8000/session?year=${selectedYear}&gp=${grandPrix}&identifier=${sessionIdentifier}`
      );
      setSessionData(response.data);
    } catch (err) {
      console.error("Error fetching session data:", err);
      setError("Failed to fetch session data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Get Session Data</h1>

      <FormWrapper onSubmit={handleSubmit}>
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
        <button type="submit">Get Session</button>
      </FormWrapper>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {sessionData && sessionData.session && loading !== true && (
        <div>
          <SectionHeading>Overview</SectionHeading>

          <SessionDetails>
            <div>
              <strong>Year</strong>
              <span>{sessionData.session.Year}</span>
            </div>
            <div>
              <strong>Grand Prix</strong>
              <span>
                {sessionData.session.GrandPrix.split(" ")
                  .map(
                    (word) =>
                      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                    //to convert forst word to upper case regardless of any input
                  )
                  .join(" ")}
              </span>
            </div>
            <div>
              <strong>Session</strong>
              <span>
                {sessionData.session.Session.split(" ")
                  .map(
                    (word) =>
                      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                  )
                  .join(" ")}
              </span>
            </div>
            <div>
              <strong>Date</strong>
              <span>{sessionData.session.Date}</span>
            </div>
            <div>
              <strong>Event Name</strong>
              <span>{sessionData.session.Event}</span>
            </div>
            <div>
              <strong>Location</strong>
              <span>{sessionData.session.Location}</span>
            </div>
          </SessionDetails>

          {sessionData.session.Results &&
          sessionData.session.Results.length > 0 ? (
            <TableWrapper>
              <StyledTable>
                <thead>
                  <tr>
                    <th>Position</th>
                    <th>Driver</th>
                    <th>Team</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Points</th>
                  </tr>
                </thead>
                <tbody>
                  {sessionData.session.Results.map((result, index) => (
                    <tr key={index}>
                      <td>{result.Position}</td>
                      <td>
                        <div className="driver-info">
                          {result.HeadshotUrl !== "None" &&
                          result.HeadshotUrl !== "" ? (
                            <img
                              src={result.HeadshotUrl}
                              alt={result.BroadcastName.toLowerCase()}
                            />
                          ) : (
                            <AvatarIcon />
                          )}
                          <span>{result.FullName}</span>
                        </div>
                      </td>
                      <td>{result.TeamName}</td>
                      <td>{result.Time || "N/A"}</td>
                      <td>{result.Status}</td>
                      <td>{result.Points}</td>
                    </tr>
                  ))}
                </tbody>
              </StyledTable>
            </TableWrapper>
          ) : (
            <p>No results available for this session.</p>
          )}
        </div>
      )}
    </PageWrapper>
  );
};

export default GetSession;
