// @ts-nocheck
import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  PageWrapper,
  FormWrapper,
  TableWrapper,
  StyledTable,
  NoDataMessage,
  Heading,
} from "./Container";
import LoadingGif from "../Icons/loading.gif";

const Circuits = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [circuits, setCircuits] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch all circuits on component mount
  useEffect(() => {
    fetchCircuits();
  }, []);

  const fetchCircuits = async (term = "") => {
    setLoading(true);
    try {
      const response = await axios.get(
        `https://anemoi-backend.onrender.com/circuits?search=${term}`
      );
      setCircuits(response.data.circuits || []);
    } catch (error) {
      console.error("Error fetching circuits:", error);
      setCircuits([]);
    }
    setLoading(false);
  };

  const handleChange = (event) => setSearchTerm(event.target.value);

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchCircuits(searchTerm);
  };

  return (
    <PageWrapper>
      <Heading>Circuits</Heading>

      <FormWrapper onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search Circuits (e.g., Catalunya)"
          value={searchTerm}
          onChange={handleChange}
        />
        <button type="submit">Search</button>
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

      {!loading && circuits.length === 0 && searchTerm && (
        <NoDataMessage>No circuits found for the search term.</NoDataMessage>
      )}

      {!loading && circuits.length > 0 && (
        <TableWrapper>
          <StyledTable>
            <thead>
              <tr>
                <th>Circuit</th>
                <th>Locality</th>
                <th>Country</th>
                <th>Latitude</th>
                <th>Longitude</th>
              </tr>
            </thead>
            <tbody>
              {circuits.map((circuit, index) => (
                <tr key={index}>
                  <td>
                    <a
                      href={circuit.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {circuit.circuitName || "N/A"}
                    </a>
                  </td>
                  <td>{circuit.Location?.locality || "N/A"}</td>
                  <td>{circuit.Location?.country || "N/A"}</td>
                  <td>{circuit.Location?.lat || "N/A"}</td>
                  <td>{circuit.Location?.long || "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </StyledTable>
        </TableWrapper>
      )}
    </PageWrapper>
  );
};

export default Circuits;
