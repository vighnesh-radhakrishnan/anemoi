import React, { useState } from "react";
import axios from "axios";
import styled from "styled-components";
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

const Standing = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [standingType, setStandingType] = useState("");
  const [standingData, setStandingData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleYearChange = (event) => {
    setSelectedYear(event.target.value);
    setStandingData(null);
  };

  const handleTypeChange = (event) => {
    setStandingType(event.target.value);
    setStandingData(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(false);
    setStandingData(null);

    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/standings?year=${selectedYear}&type=${standingType}`
      );
      if (response.data.error) {
        setError(true);
        setStandingData(null);
      } else {
        setError(false);
        setStandingData(response.data);
      }
    } catch (err) {
      console.error("Error fetching standings data:", err);
      setError(true);
      setStandingData(null); // Reset standings data in case of API errors
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <h1>Standings Data</h1>

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
        <select value={standingType} onChange={handleTypeChange} required>
          <option value="">Select Standing Type</option>
          <option value="driverStandings">Driver Standings</option>
          <option value="constructorStandings">Constructor Standings</option>
        </select>
        <button type="submit">Standings</button>
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

      {standingData && standingData.Standings && !loading && (
        <div>
          <SectionHeading>
            {standingType === "driverStandings"
              ? "Driver Standings"
              : "Constructor Standings"}{" "}
            ({standingData.Year})
          </SectionHeading>

          <TableWrapper>
            <StyledTable>
              <thead>
                <tr>
                  <th>Position</th>
                  {standingType === "driverStandings" && <th>Driver</th>}
                  {standingType === "driverStandings" && <th>Number</th>}
                  {standingType === "driverStandings" && <th>Nationality</th>}
                  <th>
                    {standingType === "driverStandings"
                      ? "Constructor"
                      : "Constructor"}
                  </th>
                  <th>
                    {standingType === "driverStandings"
                      ? "Points"
                      : "Nationality"}
                  </th>
                  <th>Points</th>
                  <th>Wins</th>
                </tr>
              </thead>
              <tbody>
                {standingData.Standings.map((item, index) => (
                  <tr key={index}>
                    <td>{item.Position}</td>
                    {standingType === "driverStandings" && item.Driver?.URL && (
                      <td>
                        <a
                          className="linked-name"
                          href={item.Driver.URL}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {item.Driver.Name}
                        </a>
                      </td>
                    )}
                    {standingType === "driverStandings" && (
                      <td>{item.Driver?.PermanentNumber || "N/A"}</td>
                    )}
                    {standingType === "driverStandings" && (
                      <td>{item.Driver?.Nationality || "N/A"}</td>
                    )}
                    <td>
                      <a
                        className="linked-name"
                        href={item.Constructor.URL}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {item.Constructor.Name}
                      </a>
                    </td>
                    <td>
                      {standingType === "driverStandings"
                        ? item.Constructor.Name
                        : item.Constructor.Nationality}
                    </td>
                    <td>{item.Points}</td>
                    <td>{item.Wins}</td>
                  </tr>
                ))}
              </tbody>
            </StyledTable>
          </TableWrapper>
        </div>
      )}

      {error && !standingData && !loading && (
        <NoDataMessage>
          Sorry, no standings data found for the provided input. Please try
          again with different values.
        </NoDataMessage>
      )}
    </PageWrapper>
  );
};

export default Standing;
