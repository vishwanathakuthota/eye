PRD.md

Eye™

AI-Native Intelligence Search Engine

Version: v0.1.0-alpha

Owner: DrPinnacle

Product Family: OpenVals

Future URL: eye.openvalidations.com

Repository: github.com/drpinnacle/eye

Status: Internal Development

⸻

Executive Summary

Eye is an AI-native intelligence search engine designed to transform publicly available information into actionable intelligence.

Unlike traditional search engines that return links and documents, Eye discovers, enriches, correlates, and explains intelligence findings.

The initial release focuses on Domain Intelligence.

Version v0.1.0-alpha is intended for local deployment, validation, architecture testing, and user experience refinement before any public release.

⸻

Vision

Search Anything.
Understand Everything.

Eye will become a unified intelligence platform capable of analyzing domains, IP addresses, organizations, individuals, threat indicators, and digital infrastructure.

The platform combines OSINT, cyber threat intelligence, risk scoring, and AI-powered summarization into a single investigative workflow.

⸻

Problem Statement

Intelligence gathering is fragmented across dozens of tools.

Analysts frequently switch between:

* WHOIS
* RDAP
* crt.sh
* VirusTotal
* Shodan
* AbuseIPDB
* AlienVault OTX
* SecurityTrails
* OpenCorporates
* News Sources

This creates inefficiency and inconsistent investigations.

Eye provides a single intelligence experience.

⸻

Product Goals

Version v0.1.0-alpha focuses on:

1. Domain Intelligence
2. Data Normalization
3. Risk Scoring
4. Investigation Reporting
5. Local Deployment Validation

⸻

Out of Scope

The following are explicitly excluded:

* Dark Web Monitoring
* Active Scanning
* Credential Collection
* Malware Execution
* Exploitation Modules
* Offensive Security Automation
* Social Engineering Capabilities

⸻

Supported Search Type

Domain Intelligence

Input:

example.com

Output:

DNS Records

RDAP Information

Certificate Transparency Data

Subdomains

Intelligence Summary

Risk Score

Investigation Report

⸻

Functional Requirements

FR-001

User can search a domain.

⸻

FR-002

System performs DNS analysis.

Supported:

A

AAAA

MX

TXT

NS

CNAME

⸻

FR-003

System performs RDAP lookup.

⸻

FR-004

System retrieves certificate transparency findings using crt.sh.

⸻

FR-005

System identifies discovered subdomains.

⸻

FR-006

System calculates risk score.

Range:

0–100

Levels:

Low

Medium

High

Critical

⸻

FR-007

System generates executive intelligence summary.

⸻

FR-008

System stores analysis results in PostgreSQL.

⸻

FR-009

System exposes REST API under:

/api/v1

⸻

FR-010

System provides dashboard interface.

⸻

Non-Functional Requirements

Performance

Average analysis time:

< 10 seconds

⸻

Reliability

95% successful analysis completion

during alpha phase.

⸻

Security

Input validation

Rate limiting

Secure secret management

Structured logging

Audit trail

⸻

Technology Stack

Frontend

Next.js

TypeScript

Tailwind CSS

⸻

Backend

FastAPI

Python

Pydantic

SQLAlchemy

Alembic

⸻

Database

PostgreSQL

⸻

Queue

Redis

Celery

⸻

Containers

Docker

Docker Compose

⸻

Architecture

Frontend

↓

API Gateway

↓

Intelligence Service

↓

Risk Engine

↓

Persistence Layer

↓

PostgreSQL

⸻

Milestone 1

Foundation

Repository

Docker

FastAPI

Next.js

Database

CI/CD

⸻

Milestone 2

Domain Intelligence

DNS

RDAP

crt.sh

Risk Engine

Persistence

⸻

Milestone 3

Dashboard

Search

Summary

Findings

Reports

History

⸻

Milestone 4

Internal Alpha

Local Deployment

Bug Fixes

Performance Testing

Security Review

⸻

Acceptance Criteria

A user enters:

example.com

Eye returns:

DNS findings

RDAP findings

Certificate findings

Subdomains

Risk score

Executive summary

Stored report

within 10 seconds.

⸻

Version Strategy

v0.1.0-alpha

Local Development

v0.2.0-alpha

Threat Intelligence Connectors

v0.3.0-beta

History + Reports

v0.4.0-beta

Authentication

v1.0.0

Public Release

eye.openvalidations.com

⸻

Product Tagline

Eye™

Search Anything.
Understand Everything.

Built by DrPinnacle.