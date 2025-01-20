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

const Constructors = () => {
  const [searchParams, setSearchParams] = useState({
    year: "",
    driverId: "",
    circuitId: "",
    country: "",
  });
  const [constructors, setConstructors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 25; // Default per page data

  // Calculate total pages
  const totalPages = Math.ceil(constructors.length / pageSize);

  // Paginated constructors
  const paginatedConstructors = constructors.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  useEffect(() => {
    fetchConstructors(); // Fetch all constructors on initial load
  }, []);

  const fetchConstructors = async () => {
    setLoading(true);
    setError("");
    try {
      const { year, driverId, circuitId, country } = searchParams;
      const query = new URLSearchParams({
        ...(year && { year }),
        ...(driverId && { driver_id: driverId }),
        ...(circuitId && { circuit_id: circuitId }),
        ...(country && { country }),
      });

      const response = await axios.get(
        `https://anemoi-backend.onrender.com/constructors?${query}`
      );
      setConstructors(response.data.constructors || []);
    } catch (error) {
      console.error("Error fetching constructors:", error);
      setError("Unable to fetch constructor data. Please check your inputs.");
    }
    setLoading(false);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setSearchParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!searchParams.year && searchParams.driverId) {
      setError("Year is required when filtering by Driver ID.");
      return;
    }
    setCurrentPage(1); // Reset to the first page
    fetchConstructors();
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <PageWrapper>
      <Heading>Constructors</Heading>

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
          name="circuitId"
          placeholder="Circuit ID (e.g., albert_park)"
          value={searchParams.circuitId}
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
      {!loading && constructors.length === 0 && (
        <NoDataMessage>
          No constructors found for the selected inputs.
        </NoDataMessage>
      )}
      {!loading && constructors.length > 0 && (
        <>
          <TableWrapper>
            <StyledTable>
              <thead>
                <tr>
                  <th>Constructor Name</th>
                  <th>Nationality</th>
                </tr>
              </thead>
              <tbody>
                {paginatedConstructors.map((constructor, index) => (
                  <tr key={index}>
                    <td>
                      <a
                        className="constructor-link"
                        href={constructor.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {constructor.name}
                      </a>
                    </td>
                    <td>{constructor.nationality || "N/A"}</td>
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

export default Constructors;
