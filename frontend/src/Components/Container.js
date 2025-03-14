// src/Components/Footer.js
import React from "react";
import styled from "styled-components";

const FooterContainer = styled.footer`
  width: 100%;
  background-color: #ffffff;
  color: #333333;
  border-top: 3px solid #e10600;
  padding: 20px 0;
  margin-top: 40px;
  position: relative;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);

  @media (max-width: 768px) {
    padding: 15px 0;
  }
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 10px;
  }
`;

const Copyright = styled.div`
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  font-size: 14px;
  letter-spacing: 0.5px;
`;

const FooterLinks = styled.div`
  display: flex;
  gap: 20px;

  @media (max-width: 768px) {
    gap: 15px;
  }
`;

const FooterLink = styled.a`
  color: #333333;
  text-decoration: none;
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  font-size: 14px;
  letter-spacing: 0.5px;
  transition: color 0.2s;

  &:hover {
    color: #e10600;
  }
`;

const FooterLogo = styled.div`
  font-family: "Titillium Web", "Segoe UI", sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: #e10600;
  letter-spacing: 1px;
`;

const Footer = () => (
  <FooterContainer>
    <FooterContent>
      <FooterLogo>ANEMOI</FooterLogo>

      <Copyright>
        Built and designed by Vighnesh Radhakrishnan. All rights reserved. ©{" "}
        {new Date().getFullYear()}
      </Copyright>

      <FooterLinks>
        <FooterLink
          href="https://github.com/vighneshradhakrishnan"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </FooterLink>
        <FooterLink
          href="https://www.linkedin.com/in/vighneshradhakrishnan"
          target="_blank"
          rel="noopener noreferrer"
        >
          LinkedIn
        </FooterLink>
      </FooterLinks>
    </FooterContent>
  </FooterContainer>
);

export default Footer;
