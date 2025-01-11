import React, { useState } from "react";
import axios from "axios";
import styled from "styled-components";
import {
  PageWrapper,
  FormWrapper,
  TableWrapper,
  StyledTable,
  LoadingMessage,
  NoDataMessage,
  Heading,
} from "./Container";

const Calendar = () => {
  const [selectedYear, setSelectedYear] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => setSelectedYear(event.target.value);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/events/${selectedYear}`
      );
      setEvents(response.data.events || []);
    } catch (error) {
      console.error("Error fetching data:", error);
      setEvents([]);
    }
    setLoading(false);
  };

  return (
    <PageWrapper>
      <Heading>Season Schedule</Heading>

      <FormWrapper onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Enter Year"
          value={selectedYear}
          onChange={handleChange}
        />
        <button type="submit">Get Calendar</button>
      </FormWrapper>

      {loading && <LoadingMessage>Loading...</LoadingMessage>}

      {!loading && events.length === 0 && selectedYear && (
        <NoDataMessage>No events found for the selected year.</NoDataMessage>
      )}

      {!loading && events.length > 0 && (
        <TableWrapper>
          <StyledTable>
            <thead>
              <tr>
                <th>Event</th>
                <th>Country</th>
                <th>Location</th>
                <th>Date</th>
                <th>Event Format</th>
                <th>Qualifying Date</th>
                <th>Race Date</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event, index) => (
                <tr key={index}>
                  <td>{event.EventName || "N/A"}</td>
                  <td>{event.Country || "N/A"}</td>
                  <td>{event.Location || "N/A"}</td>
                  <td>{event.EventDate.split(" ")[0] || "N/A"}</td>
                  <td>{event.EventFormat || "N/A"}</td>
                  <td>{event.Qualifying.split(" ")[0] || "N/A"}</td>
                  <td>{event.Race.split(" ")[0] || "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </StyledTable>
        </TableWrapper>
      )}
    </PageWrapper>
  );
};

export default Calendar;
