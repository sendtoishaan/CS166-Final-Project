-- ============================================================
-- CS166 Online Auction and Bidding System
-- Sample / Seed Data
-- ============================================================
 
-- Users (passwords are stored hashed by the app; plain here for seeding)
INSERT INTO Users (login, password, phoneNum, role, address, favoriteCategory) VALUES
('alice',   'alice123',   '951-111-2222', 'Seller', '123 Oak St, Riverside CA', 'Electronics'),
('bob',     'bob123',     '951-333-4444', 'Buyer',  '456 Pine Ave, Corona CA',   'Books'),
('carol',   'carol123',   '951-555-6666', 'Buyer',  '789 Maple Dr, Moreno Valley CA', 'Collectibles'),
('dave',    'dave123',    '951-777-8888', 'Seller', '321 Elm Blvd, Temecula CA', 'Sports'),
('eve',     'eve123',     '951-999-0000', 'Buyer',  '654 Cedar Ln, Perris CA',   'Electronics');
 
-- Items
INSERT INTO Item (itemName, category, startingPrice, description, condition, imageURL, sellerLogin) VALUES
('Vintage Polaroid Camera',   'Electronics',   25.00, 'Classic instant camera in great shape.',    'Good',      NULL, 'alice'),
('First Edition Dune Novel',  'Books',         50.00, 'First edition, some wear on cover.',        'Fair',      NULL, 'alice'),
('Nike Air Jordan 1980s',     'Sports',        75.00, 'Rare vintage sneakers, size 10.',           'Excellent', NULL, 'dave'),
('Baseball Card Collection',  'Collectibles', 100.00, '50-card lot, includes some rookies.',       'Good',      NULL, 'dave'),
('Sony Walkman TPS-L2',       'Electronics',   40.00, 'Original 1979 model, fully functional.',   'Good',      NULL, 'alice');
 
-- Auctions (Active)
INSERT INTO Auction (itemID, sellerLogin, currentHighestBid, auctionStatus) VALUES
(1, 'alice', 25.00,  'Active'),
(2, 'alice', 50.00,  'Active'),
(3, 'dave',  75.00,  'Active'),
(4, 'dave', 100.00,  'Active'),
(5, 'alice', 40.00,  'Active');
 
-- Bids
INSERT INTO Bid (auctionID, buyerLogin, bidAmount, bidTimestamp) VALUES
(1, 'bob',   30.00, NOW() - INTERVAL '2 hours'),
(1, 'carol', 35.00, NOW() - INTERVAL '1 hour'),
(1, 'eve',   42.00, NOW() - INTERVAL '30 minutes'),
(2, 'carol', 60.00, NOW() - INTERVAL '3 hours'),
(2, 'bob',   72.50, NOW() - INTERVAL '1 hour'),
(3, 'eve',   85.00, NOW() - INTERVAL '4 hours'),
(4, 'bob',  115.00, NOW() - INTERVAL '2 hours');
 
-- Update currentHighestBid to match latest bids
UPDATE Auction SET currentHighestBid = 42.00  WHERE auctionID = 1;
UPDATE Auction SET currentHighestBid = 72.50  WHERE auctionID = 2;
UPDATE Auction SET currentHighestBid = 85.00  WHERE auctionID = 3;
UPDATE Auction SET currentHighestBid = 115.00 WHERE auctionID = 4;

-- Closed auction with completed payment and delivered shipment (for demo)
INSERT INTO Bid (auctionID, buyerLogin, bidAmount, bidTimestamp) VALUES
(5, 'eve', 55.00, NOW() - INTERVAL '1 day');

UPDATE Auction SET currentHighestBid = 55.00, auctionStatus = 'Closed' WHERE auctionID = 5;

INSERT INTO Payment (auctionID, buyerLogin, amount, paymentStatus) VALUES
(5, 'eve', 55.00, 'Completed');

INSERT INTO Shipment (auctionID, address, shipmentStatus, trackingNumber) VALUES
(5, '654 Cedar Ln, Perris CA', 'Delivered', 'TRK-SAMPLE-005');

-- Closed auction awaiting buyer payment
INSERT INTO Bid (auctionID, buyerLogin, bidAmount, bidTimestamp) VALUES
(4, 'carol', 120.00, NOW() - INTERVAL '30 minutes');

UPDATE Auction SET currentHighestBid = 120.00, auctionStatus = 'Closed' WHERE auctionID = 4;

INSERT INTO Payment (auctionID, buyerLogin, amount, paymentStatus) VALUES
(4, 'carol', 120.00, 'Pending');

INSERT INTO Shipment (auctionID, address, shipmentStatus) VALUES
(4, '789 Maple Dr, Moreno Valley CA', 'Pending');

-- Closed auction with payment completed, awaiting shipment
UPDATE Auction SET auctionStatus = 'Closed' WHERE auctionID = 3;

INSERT INTO Payment (auctionID, buyerLogin, amount, paymentStatus) VALUES
(3, 'eve', 85.00, 'Completed');

INSERT INTO Shipment (auctionID, address, shipmentStatus) VALUES
(3, '654 Cedar Ln, Perris CA', 'Pending');