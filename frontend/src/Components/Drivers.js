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

const Drivers = () => {
  const [searchParams, setSearchParams] = useState({
    year: "",
    round: "",
    constructorId: "",
    circuitId: "",
    driverId: "",
  });
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 25; // Default per page data

  // Calculate total pages
  const totalPages = Math.ceil(drivers.length / pageSize);

  // Paginated drivers
  const paginatedDrivers = drivers.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  useEffect(() => {
    fetchDrivers(); // Fetch all drivers on initial load
  }, []);

  const fetchDrivers = async () => {
    setLoading(true);
    setError("");
    try {
      const { year, round, constructorId, circuitId, driverId } = searchParams;
      const query = new URLSearchParams({
        ...(year && { year }),
        ...(round && { round }),
        ...(constructorId && { constructor_id: constructorId }),
        ...(circuitId && { circuit_id: circuitId }),
        ...(driverId && { driver_id: driverId }),
      });

      const response = await axios.get(
        `https://anemoi-backend.onrender.com/drivers?${query}`
      );

      setDrivers(response.data.drivers || []);
    } catch (error) {
      console.error("Error fetching drivers:", error);
      setError("Unable to fetch driver data. Please check your inputs.");
    }
    setLoading(false);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setSearchParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setCurrentPage(1); // Reset to the first page
    fetchDrivers();
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <PageWrapper>
      <Heading>Drivers</Heading>

      <FormWrapper onSubmit={handleSubmit}>
        <input
          type="text"
          name="year"
          placeholder="Year (e.g., 2020)"
          value={searchParams.year}
          onChange={handleChange}
        />
        <input
          type="text"
          name="round"
          placeholder="Round (e.g., 5)"
          value={searchParams.round}
          onChange={handleChange}
        />
        <input
          type="text"
          name="constructorId"
          placeholder="Constructor ID (e.g., ferrari)"
          value={searchParams.constructorId}
          onChange={handleChange}
        />
        <input
          type="text"
          name="circuitId"
          placeholder="Circuit ID (e.g., monza)"
          value={searchParams.circuitId}
          onChange={handleChange}
        />
        <input
          type="text"
          name="driverId"
          placeholder="Driver ID (e.g., hamilton)"
          value={searchParams.driverId}
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
      {!loading && drivers.length === 0 && (
        <NoDataMessage>No drivers found for the selected inputs.</NoDataMessage>
      )}
      {!loading && drivers.length > 0 && (
        <>
          <TableWrapper>
            <StyledTable>
              <thead>
                <tr>
                  <th>Driver</th>
                  <th>Code Name</th>
                  <th>Date Of Birth</th>
                  <th>Nationality</th>
                </tr>
              </thead>
              <tbody>
                {paginatedDrivers.map((driver, index) => (
                  <tr key={index}>
                    <td>
                      <a
                        className="circuit-link"
                        href={driver.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {driver.givenName} {driver.familyName}
                      </a>
                    </td>
                    <td>{driver.code || "-"}</td>
                    <td>{driver.dateOfBirth || "-"}</td>
                    <td>{driver.nationality || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </StyledTable>
          </TableWrapper>

          <div style={{ textAlign: "center", marginTop: "20px" }}>
            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <span style={{ margin: "0 10px" }}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </PageWrapper>
  );
};

export default Drivers;
