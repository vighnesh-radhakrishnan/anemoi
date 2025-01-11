import React, { useState } from "react";
import axios from "axios";
import { ReactComponent as AvatarIcon } from "../Icons/avatar.svg";

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
    <div>
      <h1>F1 Session Details</h1>

      <form onSubmit={handleSubmit}>
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
      </form>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Show session details only if sessionData is available */}
      {sessionData && sessionData.session && loading !== true && (
        <div>
          <h2>Session Overview</h2>
          <p>
            <strong>Year:</strong> {sessionData.session.Year}
          </p>
          <p>
            <strong>Grand Prix:</strong> {sessionData.session.GrandPrix}
          </p>
          <p>
            <strong>Session:</strong> {sessionData.session.Session}
          </p>
          <p>
            <strong>Date:</strong> {sessionData.session.Date}
          </p>
          <p>
            <strong>Event Name:</strong> {sessionData.session.Event}
          </p>
          <p>
            <strong>Location:</strong> {sessionData.session.Location}
          </p>

          <h2>Results</h2>
          {sessionData.session.Results &&
          sessionData.session.Results.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Driver</th>
                  <th></th>
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
                    <td>{result.BroadcastName}</td>
                    <td>
                      {result.HeadshotUrl !== "None" ? (
                        <img
                          src={result.HeadshotUrl}
                          alt={result.BroadcastName.toLowerCase()}
                          style={{
                            width: "40px",
                            height: "40px",
                            borderRadius: "50%",
                          }}
                        />
                      ) : (
                        <AvatarIcon />
                      )}
                    </td>
                    <td>{result.TeamName}</td>
                    <td>{result.Time || "N/A"}</td>
                    <td>{result.Status}</td>
                    <td>{result.Points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No results available for this session.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default GetSession;
