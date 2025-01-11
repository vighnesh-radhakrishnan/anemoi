import styled from "styled-components";

export const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: futura;
  color: #333;
  h1 {
    text-align: center;
  }
`;

export const FormWrapper = styled.form`
  display: flex;
  flex-direction: row;
  gap: 15px;
  margin-bottom: 30px;
  /* font-family: futura; */

  input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    flex-grow: 1;
    font-family: futura;
  }

  button {
    padding: 10px 20px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
      background-color: #0056b3;
    }
  }
`;

export const SessionDetails = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
  padding: 20px;
  background: #f4f4f4;

  div {
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex-wrap: wrap;
    flex-grow: 1;
    margin: 10px;
  }

  strong {
    display: block;
    font-size: 0.9rem;
    color: #555;
    margin-bottom: 5px;
    text-align: center;
  }

  span {
    font-size: 1rem;
    font-weight: bold;
    color: #222;
    text-align: center;
  }
`;

export const TableWrapper = styled.div`
  overflow-x: auto;
  margin: 20px 0;
`;

export const StyledTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  /* font-family: futura; */

  th,
  td {
    padding: 15px;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f4f4f4;
    font-weight: bold;
  }

  tr:hover {
    background-color: #f9f9f9;
  }

  .driver-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;

    img {
      width: 40px;
      height: 40px;
      border-radius: 50%;
    }

    svg {
      width: 40px;
      height: 40px;
    }
  }
`;
