// src/Components/Footer.js
import React from "react";
import styled from "styled-components";

const FooterContainer = styled.footer`
  width: 100%;
  padding: 0.75rem 0;
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
`;

const FooterText = styled.p`
  margin: 0;
  font-weight: 400;
`;

const FooterLink = styled.a`
  color: #e10600;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s ease;

  &:hover {
    text-decoration: underline;
  }
`;

const Footer = () => (
  <FooterContainer>
    <FooterText>
      Built by{" "}
      <FooterLink
        href="https://github.com/vighneshradhakrishnan"
        target="_blank"
        rel="noopener noreferrer"
      >
        Vighnesh Radhakrishnan
      </FooterLink>
      . All rights reserved. © {new Date().getFullYear()}
    </FooterText>
  </FooterContainer>
);

export default Footer;
