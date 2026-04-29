# StockFlow - Inventory Management System Case Study

*Candidate:* Rajendra Suthar  
*Role:* Backend Engineering Intern  
*Company:* Bynry Inc.  
*Date:* April 29, 2026

## Project Structure

stockflow-case-study/
├── README.md
├── part1_debugging.py
├── part2_database.sql
└── part3_api.py

## Overview
This repository contains my solutions for the StockFlow 
B2B Inventory Management System case study.

### Part 1 - Code Review & Debugging
- Identified 6 critical bugs in the original code
- Fixed transaction handling, validation, and error handling

### Part 2 - Database Design
- Designed complete schema with 8 tables
- Includes audit trail, bundle support, supplier tracking

### Part 3 - API Implementation
- Low stock alert endpoint
- Handles multiple warehouses, suppliers, sales activity

## Assumptions Made
- "Recent sales" = last 30 days
- Low stock threshold stored per product
- Days until stockout = current stock ÷ avg daily sales
- Products without suppliers return null
