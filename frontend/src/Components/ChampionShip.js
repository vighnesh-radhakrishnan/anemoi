import React, { useState, useEffect } from "react";
import axios from "axios";

const Championship = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [data, setData] = useState(null);

  const handleChange = (event) => {
    setSelectedYear(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchData(selectedYear);
  };

  const fetchData = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/winners/${selectedYear}`
      );
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    if (selectedYear) fetchData(selectedYear);
  }, [selectedYear]);

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Enter Year"
          value={selectedYear}
          onChange={handleChange}
        />
        <button type="submit">Get Results</button>
      </form>

      {data ? (
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th>WDC Winner</th>
              <th>WCC Winner</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{data.year}</td>
              <td>{data.wdc}</td>
              <td>{data.wcc}</td>
            </tr>
          </tbody>
        </table>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default Championship;
