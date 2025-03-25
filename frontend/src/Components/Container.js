// @ts-nocheck
import styled from "styled-components";

export const TabWrapper = styled.div`
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;

  /* @media (max-width: 768px) {
    gap: 10px;
    margin-bottom: 15px;
  } */
`;

export const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;

  h1 {
    text-align: center;
  }

  .image-header {
    text-align: center;
    margin-bottom: 10px;
  }

  .image-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }

  .image {
    max-width: 100%;
    height: auto;
  }
  .pagination-button {
    background-color: #fff;
    color: #333;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    padding: 8px 15px;
    font-family: "Titillium Web", "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;

    &::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background-color: #e10600;
      transform: scaleX(0);
      transition: transform 0.3s ease;
      transform-origin: bottom right;
    }

    &:hover {
      color: #e10600;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);

      &::after {
        transform: scaleX(1);
        transform-origin: bottom left;
      }
    }

    &:active {
      transform: translateY(1px);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
  }

  @media (max-width: 768px) {
    padding: 10px;
    /* padding-bottom: 10px; */

    h1 {
      font-size: 1.5rem;
    }

    .image-container {
      margin-top: 10px;
    }

    .pagination-button {
      padding: 6px 12px;
      font-size: 12px;
    }
  }
`;

export const Tab = styled.div`
  padding: 10px 20px;
  background-color: ${({ active }) => (active ? "#fff" : "#e10600")};
  color: ${({ active }) => (active ? "#333" : "#fff")};
  border: 2px solid #e10600;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-size: 16px;
  font-family: futura;

  &:hover {
    background-color: #fff;
    border: 2px solid #e10600;
    color: #222;
  }

  @media (max-width: 768px) {
    padding: 8px 15px;
    font-size: 14px;
  }
`;

export const NavContainer = styled.nav`
  width: 100%;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e0e0e0;
  @media (max-width: 968px) {
    position: relative;
    border-bottom: none;
  }
`;

export const NavList = styled.ul`
  display: flex;
  justify-content: space-between;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
  @media (max-width: 968px) {
    flex-direction: column;
    align-items: flex-start;
    padding-top: 60px;
    transform: ${(props) =>
      props.isOpen ? "translateX(0)" : "translateX(-100%)"};
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 80%;
    background-color: white;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease-in-out;
    z-index: 100;
  }
`;

export const NavItem = styled.li`
  position: relative;
  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background-color: #e10600;
    transform: scaleX(0);
    transition: transform 0.3s ease;
    transform-origin: bottom right;
  }
  ${(props) =>
    props.active &&
    `
    &::after {
      transform: scaleX(1);
      transform-origin: bottom left;
    }
  `}
  &:hover::after {
    transform: scaleX(1);
    transform-origin: bottom left;
  }
  @media (max-width: 968px) {
    width: 35%;
    &::after {
      bottom: -5px;
      height: 2px;
    }
  }
  /* 
  @media (max-width: 968px) {
    width: 100%;
    margin: 5px 0;
  } */
`;

export const NavLink = styled.a`
  display: block;
  padding: 1.2rem 1rem;
  color: #333;
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  font-weight: ${(props) => (props.active ? "600" : "400")};
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s;
  &:hover {
    color: #e10600;
  }
  ${(props) =>
    props.active &&
    `
    color: #e10600;
  `}
  @media (max-width: 968px) {
    padding: 1rem 2rem;
    width: 100%;
    font-size: 16px;
  }
`;

export const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 1rem;
  @media (max-width: 968px) {
    display: block;
    position: absolute;
    right: 10px;
    top: 0;
    z-index: 101;
  }
  span {
    display: block;
    width: 25px;
    height: 3px;
    margin: 5px 0;
    position: relative;
    background: ${(props) => (props.isOpen ? "#e10600" : "#333")};
    border-radius: 3px;
    z-index: 1;
    transform-origin: 4px 0px;
    transition: transform 0.5s cubic-bezier(0.77, 0.2, 0.05, 1),
      background 0.5s cubic-bezier(0.77, 0.2, 0.05, 1), opacity 0.55s ease;
    &:first-child {
      transform-origin: 0% 0%;
      transform: ${(props) =>
        props.isOpen ? "rotate(45deg) translate(0, -1px)" : "none"};
    }
    &:nth-child(2) {
      opacity: ${(props) => (props.isOpen ? "0" : "1")};
      transform: ${(props) =>
        props.isOpen ? "rotate(0deg) scale(0.2, 0.2)" : "none"};
    }
    &:nth-child(3) {
      transform-origin: 0% 100%;
      transform: ${(props) =>
        props.isOpen ? "rotate(-45deg) translate(0, 1px)" : "none"};
    }
  }
`;

export const Overlay = styled.div`
  display: none;
  @media (max-width: 968px) {
    display: ${(props) => (props.isOpen ? "block" : "none")};
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 99;
  }
`;

export const FormWrapper = styled.form`
  display: flex;
  flex-direction: row;
  gap: 15px;
  margin-bottom: 30px;

  input,
  select {
    padding: 10px 12px;
    border: none;
    border-radius: 4px;
    font-family: "Titillium Web", "Segoe UI", sans-serif;
    font-size: 14px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
    flex-grow: 1;

    &:focus {
      outline: none;
      box-shadow: 0 1px 5px rgba(225, 6, 0, 0.2);
      border-bottom: 2px solid #e10600;
    }
  }

  select {
    color: #757575;

    option:first-child {
      color: #757575;
    }

    option:not(:first-child) {
      color: #333;
    }
  }

  input[type="number"] {
    width: 100px;
  }

  button {
    padding: 10px 20px;
    white-space: nowrap;
    background-color: #fff;
    color: #333;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-family: "Titillium Web", "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;

    &::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background-color: #e10600;
      transform: scaleX(0);
      transition: transform 0.3s ease;
      transform-origin: bottom right;
    }

    &:hover {
      color: #e10600;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);

      &::after {
        transform: scaleX(1);
        transform-origin: bottom left;
      }
    }

    &:active {
      transform: translateY(1px);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }

    &:focus {
      outline: none;
    }
  }

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 10px;
    align-items: center;

    input[type="number"] {
      width: 90%;
    }

    input[type="text"] {
      width: 90%;
    }

    select {
      width: 96%;
    }

    button {
      width: 60%;
      padding: 12px;
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

  @media (max-width: 768px) {
    flex-direction: column;
    padding: 15px 10px;

    div {
      margin: 5px 0;
    }
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

  tbody tr:nth-child(even) {
    background-color: #f9f9f9;
  }

  tbody tr:hover {
    background-color: #f1f1f1;
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
  .circuit-link {
    text-decoration: none;
  }

  .linked-name {
    text-decoration: none;
  }

  @media (max-width: 768px) {
    font-size: 0.9rem;

    th,
    td {
      padding: 10px 5px;
    }

    .driver-info {
      gap: 5px;

      img,
      svg {
        width: 30px;
        height: 30px;
      }
    }
  }
`;

export const NoDataMessage = styled.p`
  margin-top: 50px;
  text-align: center;
  color: #888;
  font-size: 1.1rem;

  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;

export const Heading = styled.h1`
  text-align: center;
  font-size: 2rem;
  color: #333;

  @media (max-width: 768px) {
    font-size: 1.5rem;
    margin: 15px 0;
  }
`;

export const FooterWrapper = styled.footer`
  width: 100%;
  padding: 0.4rem 0;
  background-color: #fff;
  color: #333;
  text-align: center;
  font-size: 0.85rem;
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  letter-spacing: 0.2px;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
  position: fixed;
  bottom: 0;
  right: 0;
  left: 0;
  z-index: 90;
  border-top: 1px solid #e0e0e0;

  @media (max-width: 968px) {
    padding: 0.6rem 0;
    font-size: 0.75rem;
  }

  a {
    color: #e10600;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s ease;

    &:hover {
      text-decoration: underline;
    }
  }
`;
