# Xiatech Agentic AI for Retail Integrations & Insights

<center>
<table>
  <tr>
    <td align="center">
      <img src="https://www.bloomreach.com/wp-content/uploads/2024/05/xiatech_logo-rgb-pos---alex-green.png" width="200"/>
    </td>
    <td align="center">
      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/La_Rochelle_Universit%C3%A9.png/1200px-La_Rochelle_Universit%C3%A9.png" width="200"/>
    </td>
  </tr>
</table>
</center>

---

## 📌 Project

This project was carried out as part of the partnership between **Xiatech** and **La Rochelle University**.  
It aims to explore the emerging concept of **Agentic AI**, an artificial intelligence capable of **not only analyzing data**, but also **making autonomous decisions and executing actions** in a retail environment.

---

## 🎯 Objective

Build a **full prototype** that enables:

- **Monitoring sales and stock levels** in near real-time.
- **Automatically identifying at-risk products** likely to run out of stock.
- **Autonomously generating purchase orders (POs)** for restocking.
- **Synchronizing automatically with an e-commerce platform** (updating stock counts and product tags).
- **Visualizing key performance indicators (KPIs)** through a React dashboard.
- **Continuously optimizing** the agent's decisions using historical feedback.

---

## 🏗️ Project Architecture

The project is based on a **full-stack architecture** with three main components:

| Component              | Technology       | Description                                                                      |
| ---------------------- | ---------------- | -------------------------------------------------------------------------------- |
| **Database**           | MongoDB          | Stores synthetic data: products, sales, stock, purchase orders, agent actions    |
| **Backend / Agent AI** | Python + FastAPI | Orchestrates autonomous workflows, calculates metrics, generates purchase orders |
| **Frontend**           | React            | Dashboard to visualize sales, stock, at-risk products, and agent actions         |

The system is orchestrated using **Docker Compose** for easy local deployment.

---

## ⚙️ Main Features

1. **Daily sales and stock analysis**

   - Aggregate sales by SKU
   - Calculate remaining stock time before depletion
   - Identify “at-risk” products (< 3 days of stock remaining)

2. **Automated restocking**

   - Generate **Purchase Orders** for at-risk products
   - Record orders in MongoDB

3. **E-commerce updates**

   - Dynamically adjust stock levels
   - Add or remove “at-risk” tags

4. **Tracking and KPIs**

   - Stockout rate
   - Number and quantity of generated POs
   - History of agent actions

5. **Interactive user interface**
   - React dashboard to visualize data
   - Button to manually trigger the agent
   - Real-time view of actions and metrics

---

## 🛠️ Installation & Setup

1. **Clone the repository**

```bash
git clone git@gitlab.univ-lr.fr:project-xiatech/project_xiatech.git
cd project_xiatech
```

## 🙇 Author

**Lilian Mirabel – Florian Chapoullie-Pino – Luc Lacotte – Floris Rimbeau**
