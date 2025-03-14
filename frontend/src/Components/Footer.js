// src/Components/Footer.js
import React from "react";
import styled from "styled-components";

const FooterContainer = styled.footer`
  width: 100%;
  padding: 1.5rem 0;
  background-color: #fff;
  color: #333;
  text-align: center;
  font-size: 0.9rem;
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  letter-spacing: 0.5px;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
  position: fixed;
  bottom: 0;
  right: 0;
  left: 0;
  z-index: 90;
  border-top: 1px solid #e0e0e0;

  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background-color: #e10600;
  }

  @media (max-width: 968px) {
    padding: 1rem 0;
    font-size: 0.8rem;
  }
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: center;
  align-items: center;

  @media (max-width: 968px) {
    flex-direction: column;
    gap: 0.5rem;
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
    <FooterContent>
      <FooterText>
        Built and designed by{" "}
        <FooterLink
          href="https://github.com/vighneshradhakrishnan"
          target="_blank"
          rel="noopener noreferrer"
        >
          Vighnesh Radhakrishnan
        </FooterLink>
        . All rights reserved. © {new Date().getFullYear()}
      </FooterText>
    </FooterContent>
  </FooterContainer>
);

export default Footer;
