---
doc_id: KB-ORD-001
title: Account and Order Help
category: account_orders
products:
  - all
locale: en-US
version: "1.0.0"
effective_date: "2026-01-15"
access_level: public
---

# Account and Order Help

## General Help Versus Private Order Help
<!-- section_id: KB-ORD-001-general-vs-private-help -->

Anyone may ask about published products and policies. Viewing or changing a specific order requires authenticated ownership. An order number, name, postal address, or email address typed into chat is not sufficient authentication by itself.

A signed-in customer is authenticated only when the trusted session supplies a verified customer ID. A guest purchaser must complete Acme Audio's secure order-verification flow using the order number and purchase email. Guest verification is outside the Version 1 automated workflow, so the agent must use the secure support handoff. It may direct the customer to the secure flow but must not ask the customer to paste a password or one-time code into chat.

After verification, support may access only orders whose owner ID or verified guest-order ID matches the trusted session. If ownership does not match, support must neither disclose order details nor confirm whether the order exists.

## Order Statuses
<!-- section_id: KB-ORD-001-order-statuses -->

| Status | Meaning | Customer-facing actions |
| --- | --- | --- |
| `PROCESSING` | Payment accepted; warehouse work not locked | Cancellation or address correction may be requested but is not guaranteed |
| `PACKED` | Warehouse lock recorded | Items, address, and cancellation cannot be changed |
| `SHIPPED` | Carrier label and handoff are in progress or complete | Use tracking; order cannot be edited or cancelled |
| `DELIVERED` | Carrier recorded delivery | Apply delivery-problem or return policy as appropriate |
| `CANCELLED` | Order was cancelled before shipment | No shipment will occur; payment release timing depends on the issuer |

Support must use the current order record rather than infer status from the customer's description.

## Cancellations and Order Changes
<!-- section_id: KB-ORD-001-cancellations-and-changes -->

A cancellation or shipping-address correction can succeed only while an order is `PROCESSING` and before the warehouse lock. If the state changes to `PACKED` before the request is committed, the request fails. Support must explain that a request is not a guarantee until the order record confirms it.

Items, quantities, discounts, and payment methods cannot be edited after checkout. While an order remains cancellable, the customer may request cancellation and place a new order with the correct details. Once shipped, the customer may use the return process after delivery if eligible.

Support must never redirect a shipped parcel to a different address. Carrier reroute requests and any address that differs from the verified order require fraud-risk escalation.

The Version 1 automated agent cannot cancel an order, change an address, edit an order, or initiate a carrier reroute. If a verified customer's `PROCESSING` order may still qualify for cancellation or address correction, the agent must use the secure support handoff and must not claim that the request is complete. A handoff does not pause warehouse processing or guarantee success.

## Order Lookup and Documents
<!-- section_id: KB-ORD-001-order-lookup-and-documents -->

After ownership verification, support may provide the current status, purchased items, non-sensitive destination summary, tracking link, and order invoice. Payment information must be limited to the brand and last four digits already returned by the approved order tool. Full payment numbers and security codes are never available to support.

Invoices are fixed records. A customer may update their account profile for future orders, but support must not rewrite the billing identity or address on a completed invoice.

The Version 1 automated agent may read only the authenticated customer's minimal order and shipment views returned by approved ownership-enforcing tools. Sending or regenerating an invoice, updating a profile, and any other account or order write are unsupported; the agent must use the secure support handoff without claiming completion.

## Delivery and Item Problems
<!-- section_id: KB-ORD-001-delivery-and-item-problems -->

- Apply `KB-SHIP-001` for late, missing, damaged, or incorrect shipments.
- A missing or incorrect item should be reported within seven calendar days of delivery.
- A package marked delivered but not found should be checked and reported within 14 calendar days of the delivery scan.
- Apply `KB-RET-001` for preference returns and refunds.
- Apply `KB-WAR-001` for suspected manufacturing defects outside the return window.

Order ownership must be verified before support opens a trace, reveals shipment events, proposes a return, or creates a support case containing order data.

## Account Access
<!-- section_id: KB-ORD-001-account-access -->

Support may send the standard password-reset link to the account email through the approved account service. Support cannot see passwords, choose a new password, disable multi-factor authentication, or change an account email in chat. A customer who cannot access the registered email must use the secure account-recovery process.

Sending a password-reset message and making any account change are outside the Version 1 automated workflow. The automated agent must direct the customer to the secure self-service or support handoff; it must never claim that it sent a reset, changed an email address, or changed multi-factor authentication.

## Version 1 Automated-Agent Boundaries
<!-- section_id: KB-ORD-001-v1-agent-boundaries -->

The automated agent may answer public account and order policy questions and, for a signed-in customer whose trusted session supplies the owning customer ID, read the minimal order and shipment status returned by approved tools. It may also evaluate a return and prepare a proposed return under `KB-RET-001`.

It cannot authenticate from chat content, complete guest or gift-recipient verification, cancel or edit orders, reroute shipments, send account messages or documents, update profiles, change credentials, create a non-return support case, issue a refund or store credit, or perform any other external write. These requests require the secure support handoff. Return creation is the only Version 1 write and still requires the documented human review before execution.

## Related Documents
<!-- section_id: KB-ORD-001-related-documents -->

- `KB-SHIP-001` — Shipping and Delivery Policy
- `KB-RET-001` — Returns and Refunds Policy
