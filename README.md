# CS166 Online Auction and Bidding System Final Project

A web-based online aution platform where users can open or join autions, list items, and place bids along with completing auction payments and shipment flow. This project is a three-tier application built upon PostgreSQL.

## Project Structure:
CS166-Final-Project/
├── MAIN_STREAMLIT_UI.py
├── DATABASE_CONNECTION.py
├── AUTHENTICATION.py
├── USERS.py
├── ITEMS.py
├── AUCTIONS.py
├── BIDS.py
├── PAYMENTS.py
├── AUCTION_AND_BIDDING_SCHEMA.sql
├── SAMPLE_AUCTION_AND_BIDDING_DATA.sql
└── README.md

## Features:
- Accounts and Authentication: user registration and login using SHA-256 hashed passwords for security/authentication.
- Role-based Permissions: three different account roles('Buyer', 'Seller', and 'Admin').
- List Items: accounts with 'Seller' role permissions can create and list items along with its category, price, condition, and a description.
- Start/open Auctions: auctions can be created for an item (limited to one active auction per item). Users are able to browse, search, and filter active autions.
- Place Bids: accounts with 'Buyer' role permissions can place bids that have been validated, meaning that their bid must exceed the current highest bid. However, sellers cannot bid on their own listed items.
- End/close Auctions: when an auction is closed or ends the auction picks the winning bid (current highest bid using the timestamp as a tie-breaker) and automatically creates a pending payment and shipment.
- Payment and Shipments: track payment and shipment statuses.
- Admin Controls: Controls that allow accounts with 'Admin' role permissions to view and edit other role accounts, auctions, and payments.

## Tools Used:
- Programming Language: Python 3.10+
- Frontend: Streamlit
- Database and Database Driver: PostgreSQL 14+ and psycopg2

## Prerequisites
- Python 3.10 or newer
- Running PostgreSQL 14+ server

## Setup:
1. Clone github repo and enter project folder
- git clone https://github.com/sendtoishaan/CS166-Final-Project.git
- cd CS166-Final-Project
2. Create virtual environment and install dependencies
- python -m venv venv
if on macOS/Linux:
- source venv/bin/activate
if on Windows:
- .\venv\Scripts\Activate.ps1
- pip install streamlit psycopg2-binary
3. Create database and load schema with sample data:
- createdb CS166_AUCTION_AND_BIDDING_DATABASE
- psql -d CS166_AUCTION_AND_BIDDING_DATABASE -f AUCTION_AND_BIDDING_SCHEMA.sql
- psql -d CS166_AUCTION_AND_BIDDING_DATABASE -f SAMPLE_AUCTION_AND_BIDDING_DATA.sql
4. Configure database connection:
if on macOS/Linux:
- export DB_USER=postgres
- export DB_PASSWORD=yourpassword
if on Windows:
- $env:DB_USER="postgres"
- $env:DB_PASSWORD="yourpassword"
5. Run Streamlit App:
- streamlit run MAIN_STREAMLIT_UI.py
- Open 'https://localhost:8501' in browser

## Accounts:
- Admin-role Account:
- User: admin
- Password: admin123
- Preset Name: alice, alice123
- Seller-role Account:
- User1: dave
- Password1: dave123

- User2: bob
- Password2: bob123
- Buyer-role Account:
- User: eve
- Password2: eve123

## System Rules:
- Only an account with the 'Buyer' role can see the bid form and place bids.
- A newly placed bid on an item in an auction must be greater than the current highest bid.
- Payment and Shipment pages are empty until an auction is manually or automatically closed.
- An item can only be listed to one active auction at a time.

## Database Schema:
- Database is built with six tables. Primary keys are bold and foreign keys are marked with -> with their referenced table.

### Users table
- Sorts all three different types of account: Buyers, Sellers, and Admins

| Column | Type | Notes |
|--------|------|-------|
| **login** | VARCHAR(50) | Primary key (the username) |
| password | VARCHAR(255) | SHA-256 hash (stored by the app) |
| phoneNum | VARCHAR(20) | Required |
| role | VARCHAR(10) | `Buyer` \| `Seller` \| `Admin`, defaults to `Buyer` |
| address | TEXT | Required; used as the default shipment address |
| favoriteCategory | VARCHAR(100) | Optional |

### Item Table
- An item listed by a seller that exists independently of auctions.

| Column | Type | Notes |
|--------|------|-------|
| **itemID** | SERIAL | Primary key |
| itemName | VARCHAR(255) | Required |
| category | VARCHAR(100) | Required |
| startingPrice | NUMERIC(12,2) | Required, must be ≥ 0 |
| description | TEXT | Optional |
| condition | VARCHAR(50) | Optional (e.g. New, Good, Fair) |
| imageURL | TEXT | Optional |
| sellerLogin | VARCHAR(50) | → Users (ON DELETE CASCADE) |

### Auction Table
- An active or closed sale for an item.

| Column | Type | Notes |
|--------|------|-------|
| **auctionID** | SERIAL | Primary key |
| itemID | INTEGER | → Item (ON DELETE CASCADE) |
| sellerLogin | VARCHAR(50) | → Users |
| currentHighestBid | NUMERIC(12,2) | Cached high bid; starts at the item's price |
| auctionStatus | VARCHAR(10) | `Active` \| `Closed`, defaults to `Active` |
| createdAt | TIMESTAMP | Defaults to the creation time |


### Bid Table
- Each individual bid plabed by a buyer on an auction

| Column | Type | Notes |
|--------|------|-------|
| **bidID** | SERIAL | Primary key |
| auctionID | INTEGER | → Auction (ON DELETE CASCADE) |
| buyerLogin | VARCHAR(50) | → Users |
| bidAmount | NUMERIC(12,2) | Required, must be > 0 |
| bidTimestamp | TIMESTAMP | Defaults to the time placed |

### Payment Table
- Table that is automatically created when an aution with a winning bid is closed.

| Column | Type | Notes |
|--------|------|-------|
| **paymentID** | SERIAL | Primary key |
| auctionID | INTEGER | → Auction |
| buyerLogin | VARCHAR(50) | → Users (the winner) |
| amount | NUMERIC(12,2) | Required, must be > 0 |
| paymentStatus | VARCHAR(10) | `Pending` \| `Completed` \| `Failed`, defaults to `Pending` |

### Shipment Table
- Table that is automatically created when an auction with a winning bid is closed and also tracks delivery of the purchased item.

| Column | Type | Notes |
|--------|------|-------|
| **shipmentID** | SERIAL | Primary key |
| auctionID | INTEGER | → Auction |
| address | TEXT | Defaults to the winning buyer's address |
| shipmentStatus | VARCHAR(10) | `Pending` \| `Shipped` \| `Delivered`, defaults to `Pending` |
| trackingNumber | VARCHAR(100) | Optional |

### Relationships
- A **user** can own many **items** and open/start many **auctions**.
- An **item** can have many **auctions**, but only one active **auction** at one time.
- An **auction** has many **bids** and a **user** can place many **bids**.
- Closing an auction automatically creates one **payment** and one **shipment** corresponding to the winning bid.
