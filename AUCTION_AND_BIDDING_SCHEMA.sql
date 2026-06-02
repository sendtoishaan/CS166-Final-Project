-- ============================================================
-- CS166 Online Auction and Bidding System
-- Phase 2: Relational Schema (PostgreSQL)
-- ============================================================
 
-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS Shipment CASCADE;
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS Bid CASCADE;
DROP TABLE IF EXISTS Auction CASCADE;
DROP TABLE IF EXISTS Item CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
 
-- ============================================================
-- Users
-- ============================================================
CREATE TABLE Users (
    login           VARCHAR(50)  PRIMARY KEY,
    password        VARCHAR(255) NOT NULL,
    phoneNum        VARCHAR(20)  NOT NULL,
    role            VARCHAR(10)  NOT NULL DEFAULT 'Buyer'
                        CHECK (role IN ('Buyer', 'Seller', 'Admin')),
    address         TEXT         NOT NULL,
    favoriteCategory VARCHAR(100)
);
 
-- ============================================================
-- Item
-- ============================================================
CREATE TABLE Item (
    itemID          SERIAL       PRIMARY KEY,
    itemName        VARCHAR(255) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    startingPrice   NUMERIC(12,2) NOT NULL CHECK (startingPrice >= 0),
    description     TEXT,
    condition       VARCHAR(50),
    imageURL        TEXT,
    sellerLogin     VARCHAR(50)  NOT NULL REFERENCES Users(login) ON DELETE CASCADE
);
 
-- ============================================================
-- Auction
-- ============================================================
CREATE TABLE Auction (
    auctionID           SERIAL        PRIMARY KEY,
    itemID              INTEGER       NOT NULL REFERENCES Item(itemID) ON DELETE CASCADE,
    sellerLogin         VARCHAR(50)   NOT NULL REFERENCES Users(login),
    currentHighestBid   NUMERIC(12,2) NOT NULL DEFAULT 0,
    auctionStatus       VARCHAR(10)   NOT NULL DEFAULT 'Active'
                            CHECK (auctionStatus IN ('Active', 'Closed')),
    createdAt           TIMESTAMP     NOT NULL DEFAULT NOW()
);
 
-- ============================================================
-- Bid
-- ============================================================
CREATE TABLE Bid (
    bidID           SERIAL        PRIMARY KEY,
    auctionID       INTEGER       NOT NULL REFERENCES Auction(auctionID) ON DELETE CASCADE,
    buyerLogin      VARCHAR(50)   NOT NULL REFERENCES Users(login),
    bidAmount       NUMERIC(12,2) NOT NULL CHECK (bidAmount > 0),
    bidTimestamp    TIMESTAMP     NOT NULL DEFAULT NOW()
);
 
-- ============================================================
-- Payment
-- ============================================================
CREATE TABLE Payment (
    paymentID       SERIAL        PRIMARY KEY,
    auctionID       INTEGER       NOT NULL REFERENCES Auction(auctionID),
    buyerLogin      VARCHAR(50)   NOT NULL REFERENCES Users(login),
    amount          NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    paymentStatus   VARCHAR(10)   NOT NULL DEFAULT 'Pending'
                        CHECK (paymentStatus IN ('Pending', 'Completed', 'Failed'))
);
 
-- ============================================================
-- Shipment
-- ============================================================
CREATE TABLE Shipment (
    shipmentID      SERIAL        PRIMARY KEY,
    auctionID       INTEGER       NOT NULL REFERENCES Auction(auctionID),
    address         TEXT          NOT NULL,
    shipmentStatus  VARCHAR(10)   NOT NULL DEFAULT 'Pending'
                        CHECK (shipmentStatus IN ('Pending', 'Shipped', 'Delivered')),
    trackingNumber  VARCHAR(100)
);
 
-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX idx_auction_status   ON Auction(auctionStatus);
CREATE INDEX idx_auction_seller   ON Auction(sellerLogin);
CREATE INDEX idx_bid_auction      ON Bid(auctionID);
CREATE INDEX idx_bid_buyer        ON Bid(buyerLogin);
CREATE INDEX idx_item_seller      ON Item(sellerLogin);
CREATE INDEX idx_item_category    ON Item(category);
CREATE INDEX idx_payment_auction  ON Payment(auctionID);
CREATE INDEX idx_shipment_auction ON Shipment(auctionID);
 
-- ============================================================
-- Seed: Default Admin account
-- Password stored as plain text here; app hashes on first login
-- ============================================================
INSERT INTO Users (login, password, phoneNum, role, address)
VALUES ('admin', 'admin123', '000-000-0000', 'Admin', 'System');