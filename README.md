# Delivery-Service-Python

## Introduction

This system is designed for a new food company aiming to provide online food delivery services. It supports both **Home Delivery** and **Takeaway** orders, manages a dedicated fleet of delivery agents, and offers real-time updates on estimated order completion times. Customers can place multiple orders at once, while restaurant managers can monitor key metrics through a dedicated dashboard. The system ensures data persistence across multiple CLI sessions using file-based storage.

## Functional Requirements

### Order Types
- The system accommodates both **Home Delivery** and **Takeaway** orders.
- Home Delivery orders have an estimated delivery time of **30 minutes**.
- Takeaway orders have an estimated pickup time of **10 minutes**.

### Order Management
- Customers can place multiple orders simultaneously.
- Orders must include at least one menu item with a positive quantity.
- Only items from the pre-defined menu can be ordered.
- The system calculates and displays the estimated time for each order.
- Customers can track the status and time remaining for their orders.

### Delivery Agent Management
- A fleet of delivery agents is managed by the system.
- Home Delivery orders are assigned to the first available delivery agent.

### Manager Dashboard (Restaurant POV)
- Managers can log in using fixed credentials.
- The dashboard provides insights, including:
  - Total number of orders.
  - Breakdown of Home Delivery vs. Takeaway orders.
  - Revenue calculation based on menu prices.
  - Average estimated delivery/pickup time.

### Data Persistence
- The system maintains data persistence (customers, orders, and delivery assignments) using **file-based storage** (Python’s `pickle` module), ensuring shared data across CLI sessions.

## Non-Functional Requirements

- **Usability:** The CLI interface is user-friendly, featuring clear prompts and error messages.
- **Reliability:** All user inputs are validated, and errors (e.g., duplicate registration, invalid order details) are managed gracefully.
- **Maintainability:** The system is modular, with distinct classes handling different functions (e.g., Customer, Order, DeliveryAgent, Manager).
- **Performance:** The application efficiently processes user input and manages data persistence without delays.

## Major Use Cases

### 4.1 Customer Registration and Login  
**ID:** UCR-0001  
**Description:**  
Customers can register by providing their details (username, password, email, full name, address, and phone). The system ensures unique and correctly formatted inputs. Later, they can log in using their credentials.  

**Primary Actor:** Customer  
**Stakeholders:**  
- **Customer:** Requires a smooth registration and login experience.  
- **Business:** Needs accurate and unique customer records.  
- **Administrator:** Ensures data integrity through validation.  

**Preconditions:**  
- The system is active and accessible.  
- The customer has valid registration details.  

**Postconditions:**  
- A new customer record is created and stored persistently.  
- Successful authentication upon login.  

**Main Flow:**  
1. Customer selects "Register".  
2. System prompts for username, password, email, full name, address, and phone number.  
3. Customer provides details.  
4. System validates the input (checking for duplicates and email format) and registers the customer.  
5. Customer logs in with credentials and gains access.  

**Alternate Flows:**  
- If the username/email is already taken, the system prompts for new details.  
- If an invalid email format is entered, an error message is displayed.  
- Incorrect login credentials result in an error message.

---

### 4.2 Placing an Order  
**ID:** UO-0002  
**Description:**  
A logged-in customer selects items from a predefined menu, specifies quantities, and chooses an order type (Home Delivery or Takeaway). The system validates the order, calculates an estimated time (30 minutes for Home Delivery, 10 minutes for Takeaway), and generates a unique order ID.  

**Primary Actor:** Customer  
**Stakeholders:**  
- **Customer:** Expects accurate pricing and time estimates.  
- **Business:** Requires smooth order processing.  
- **Delivery Agents:** Need timely assignment for Home Delivery orders.  

**Preconditions:**  
- The customer is logged in.  
- The product menu is available.  
- The shopping cart is accessible and initially empty.  

**Postconditions:**  
- A new order is created with a unique ID.  
- The estimated delivery/pickup time is displayed.  
- For Home Delivery, a delivery agent is assigned.  

**Main Flow:**  
1. Customer selects "Place Order".  
2. System displays the menu with prices.  
3. Customer selects items and quantities.  
4. Customer chooses an order type.  
5. System validates the order and calculates the estimated time.  
6. Order is confirmed and stored.  
7. If Home Delivery, the first available delivery agent is assigned.  

**Alternate Flows:**  
- If invalid items/quantities are entered, the system rejects the order.  
- If the cart is empty, checkout is not allowed.  
- If a discount coupon is applied, the system verifies its validity before applying it.

---

### 4.3 Viewing Order Status  
**ID:** UO-0003  
**Description:**  
Customers can check their order history, including order IDs, current status, and estimated time remaining.  

**Primary Actor:** Customer  
**Stakeholders:**  
- **Customer:** Wants to track their order progress.  
- **Business:** Uses order status for operational insights.  

**Preconditions:**  
- The customer is logged in.  
- At least one order has been placed.  

**Postconditions:**  
- Customers view real-time order updates.  

**Main Flow:**  
1. Customer selects "View Order Status".  
2. System retrieves and displays the customer’s order history.  
3. Order details (ID, type, status, time remaining) are shown.  

**Alternate Flows:**  
- If no orders exist, the system notifies the customer.

---

### 4.4 Delivery Agent Assignment & Status Updates  
**ID:** UDA-0004  
**Description:**  
For Home Delivery orders, the system assigns the first available agent. The agent updates the order status as it progresses (e.g., "En Route", "Delivered").  

**Primary Actor:** System/Delivery Agent  
**Stakeholders:**  
- **Customer:** Needs timely updates.  
- **Business:** Ensures efficient order fulfillment.  
- **Delivery Agent:** Needs an interface to update statuses.  

**Preconditions:**  
- A Home Delivery order has been placed.  
- Available delivery agents exist.  

**Postconditions:**  
- An agent is assigned to the order.  
- Order status updates are visible to customers.  

**Main Flow:**  
1. System assigns an available agent when a Home Delivery order is placed.  
2. Agent updates the order status.  
3. Updated status is displayed to the customer.  

**Alternate Flows:**  
- If no agents are available, the system delays assignment or notifies the customer.  
- If an agent fails to update, the last known status is retained.

---

### 4.5 Manager Dashboard  
**ID:** UMD-0005  
**Description:**  
Managers can log in to view a dashboard summarizing total orders, order breakdown, revenue, and average estimated times.  

**Primary Actor:** Manager  
**Stakeholders:**  
- **Manager:** Requires operational insights.  
- **Business:** Uses data for strategic planning.  

**Preconditions:**  
- Manager has valid credentials.  
- Order data exists.  

**Postconditions:**  
- The dashboard displays aggregated metrics.  

**Main Flow:**  
1. Manager logs in.  
2. System compiles order, revenue, and time data.  
3. Dashboard report is displayed.  

**Alternate Flows:**  
- If no data exists, the system notifies the manager.

---

### 4.6 Persistent Data Storage  
**ID:** UPA-0006  
**Description:**  
The system uses **file-based storage** (`pickle` module) to save data, ensuring continuity between CLI sessions.  

**Primary Actor:** System/All Users  
**Stakeholders:**  
- **Users:** Expect data retention.  
- **Business:** Needs reliable storage.  

**Preconditions:**  
- The persistence file exists.  

**Postconditions:**  
- System state is saved and restored between sessions.  

**Main Flow:**  
1. Data is stored in memory during interactions.  
2. System saves data to a file.  
3. On startup, system loads saved data.  

**Alternate Flows:**  
- If the file is missing or corrupted, the system initializes a new state and logs a warning.

---

**Assumptions:**  
- The menu is pre-defined.  
- Persistence is managed via a single pickle file.  
- Manager credentials: `manager / manager123`.

## Running the App and Tests

### How to run

```
python3 main.py
```

### How to testcases

```
python3 -m testcases.test_food_delivery
```


## Test Cases

### User Authentication
1. **Customer Registration Success**: Tests successful customer registration with valid credentials
2. **Duplicate Registration**: Verifies system rejects registration with existing username
3. **Customer Login Success**: Tests successful login with correct credentials
4. **Customer Login Wrong Password**: Verifies login rejection with incorrect password
5. **Customer Login Nonexistent**: Tests handling of login with non-existent username

### Order Placement
6. **Place Home Delivery Order Success**: Tests successful home delivery order placement
7. **Place Takeaway Order Success**: Tests successful takeaway order placement
8. **Place Order Empty Items**: Verifies rejection of orders with no items
9. **Place Order Invalid Order Type**: Tests handling of invalid order type
10. **Order With Negative Quantity**: Verifies rejection of orders with negative quantities
11. **Invalid Menu Item In Order**: Tests handling of non-menu items in orders

### Order Time Calculation
12. **Order Estimated Time Home Delivery**: Tests correct estimation for home delivery orders
13. **Order Estimated Time Takeaway**: Tests correct estimation for takeaway orders
14. **Time Left Format**: Verifies correct formatting of remaining time

### Order Management
15. **Cancel Order Already Delivered**: Verifies rejection of cancellation for delivered orders
16. **Order History By Date Range**: Tests filtering orders by date range
17. **Order Calculate Total**: Tests correct calculation of order total cost
18. **Get Order Details**: Tests retrieval of detailed order information

### Delivery Agent Management
19. **Delivery Agent Assignment**: Tests automatic assignment of delivery agents to orders
20. **Delivery Agent Is Available**: Tests availability status of delivery agents
21. **Delivery Agent Update Status**: Tests updating order status through delivery agents

### Manager Dashboard
22. **Manager Dashboard Report**: Tests generation of restaurant dashboard report
23. **Manager Login Credentials**: Verifies fixed manager credentials
24. **Manager Generate Popular Items Report**: Tests generation of popular items report

### Customer Features
25. **Multiple Orders Same Customer**: Tests tracking multiple orders for one customer
26. **Customer Update Profile**: Tests customer profile information updates
27. **Customer Notification Setting**: Tests enabling/disabling customer notifications
28. **Rate Order**: Tests order rating functionality

### Special Features
29. **Add Special Instructions To Order**: Tests adding special instructions to orders
30. **Order With Discount**: Tests application of percentage discounts to orders
31. **Order With Invalid Discount**: Verifies rejection of invalid discount values
32. **Apply Promo Code**: Tests application of promotional codes to orders
33. **Invalid Promo Code**: Tests handling of invalid promo codes

### System Persistence
34. **Persistence After Order**: Tests data persistence between system restarts
35. **Registration Invalid Parameters**: Tests validation of registration parameters
