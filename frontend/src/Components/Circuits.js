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
  const [searchParams, setSearchParams] = useState({
    year: "",
    driverId: "",
    constructorId: "",
    country: "",
  });
  const [circuits, setCircuits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchCircuits = async () => {
    setLoading(true);
    setError("");
    try {
      const { year, driverId, constructorId, country } = searchParams;
      const query = new URLSearchParams({
        ...(year && { year }),
        ...(driverId && { driver_id: driverId }),
        ...(constructorId && { constructor_id: constructorId }),
        ...(country && { country }),
      });

      const response = await axios.get(
        `https://anemoi-backend.onrender.com/circuits?${query}`
      );
      setCircuits(response.data.circuits || []);
    } catch (error) {
      console.error("Error fetching circuits:", error);
      setError("Unable to fetch circuit data. Please check your inputs.");
    }
    setLoading(false);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setSearchParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!searchParams.driverId && searchParams.constructorId) {
      setError("Driver ID and Constructor ID are both required.");
      return;
    }
    fetchCircuits();
  };

  return (
    <PageWrapper>
      <Heading>Circuits</Heading>

      <FormWrapper onSubmit={handleSubmit}>
        <input
          type="text"
          name="year"
          placeholder="Year (e.g., 2010)"
          value={searchParams.year}
          onChange={handleChange}
        />
        <input
          type="text"
          name="driverId"
          placeholder="Driver ID (e.g., alonso)"
          value={searchParams.driverId}
          onChange={handleChange}
        />
        <input
          type="text"
          name="constructorId"
          placeholder="Constructor ID (e.g., mclaren)"
          value={searchParams.constructorId}
          onChange={handleChange}
        />
        <input
          type="text"
          name="country"
          placeholder="Country (e.g., Australia)"
          value={searchParams.country}
          onChange={handleChange}
        />
        <button type="submit">Search</button>
      </FormWrapper>

      {error && <NoDataMessage>{error}</NoDataMessage>}
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
      {!loading && circuits.length === 0 && (
        <NoDataMessage>
          No circuits found for the selected inputs.
        </NoDataMessage>
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
                      className="circuit-link"
                      href={circuit.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {circuit.circuitName}
                    </a>
                  </td>
                  <td>{circuit.locality || "N/A"}</td>
                  <td>{circuit.country || "N/A"}</td>
                  <td>{circuit.lat || "N/A"}</td>
                  <td>{circuit.long || "N/A"}</td>
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
